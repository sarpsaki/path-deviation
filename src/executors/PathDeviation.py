"""
    Calculates the Fréchet distance between each tracked object's actual trajectory
    and a user-defined reference path, enabling path compliance monitoring and
    route deviation detection across video frames.
"""
import sys
import os
import json
from typing import Optional

sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../"))

from sdks.novavision.src.base.capsule import Capsule
from sdks.novavision.src.helper.executor import Executor
from capsules.PathDeviation.src.utils.response import build_response
from capsules.PathDeviation.src.models.PackageModel import PackageModel
from capsules.PathDeviation.src.utils.frechet import frechet_distance, get_anchor_point


class PathDeviation(Capsule):

    def __init__(self, request, bootstrap):
        super().__init__(request, bootstrap)
        self.request.model = PackageModel(**self.request.data)

        self.image          = self.request.get_param("inputImage")
        self.video_id       = self._extract_video_id(self.image)
        self.detections     = self.request.get_param("inputDetections") or []
        self.anchor         = self.request.get_param("configTriggeringAnchor") or "CENTER"
        self.reference_path = self._parse_reference_path(
            self.request.get_param("configReferencePath") or "[[0,0],[100,100]]"
        )

        self.outputData = []

    @staticmethod
    def bootstrap(config: dict) -> dict:
        return {'pathStore': {}}

    @staticmethod
    def _extract_video_id(image) -> str:
        try:
            return str(image.video_metadata.video_identifier)
        except Exception:
            try:
                return str(image.uID)
            except Exception:
                return "default"

    @staticmethod
    def _parse_reference_path(raw: str) -> list:
        try:
            parsed = json.loads(raw)
            return [tuple(pt) for pt in parsed]
        except Exception as e:
            print(f"[PathDeviation] Referans yol parse hatası: {e}. Varsayılan kullanılıyor.")
            return [(0, 0), (100, 100)]

    @staticmethod
    def _get_tracker_id(det: dict) -> Optional[str]:
        tid = det.get("tracker_id") or det.get("trackerId")
        if tid is not None:
            return str(tid)
        img_uid = det.get("imgUID")
        if img_uid:
            label = det.get("classLabel", "obj")
            bbox  = det.get("boundingBox", {})
            left  = int(bbox.get("left", det.get("left", 0)))
            top   = int(bbox.get("top",  det.get("top",  0)))
            return f"{label}_{left}_{top}"
        return None

    def _get_or_create_history(self, tracker_id: str) -> list:
        path_store  = self.bootstrap.setdefault('pathStore', {})
        video_paths = path_store.setdefault(self.video_id, {})
        if tracker_id not in video_paths:
            video_paths[tracker_id] = []
        return video_paths[tracker_id]

    def _compute_deviation(self, path_history: list) -> float:
        if len(path_history) < 2:
            return 0.0
        try:
            return frechet_distance(path_history, self.reference_path)
        except Exception as e:
            print(f"[PathDeviation] Fréchet hesaplama hatası: {e}")
            return 0.0

    def run(self):
        for det in self.detections:
            tracker_id = self._get_tracker_id(det)
            enriched   = dict(det)

            if tracker_id is None:
                enriched["path_deviation"] = None
                self.outputData.append(enriched)
                continue

            history      = self._get_or_create_history(tracker_id)
            anchor_point = get_anchor_point(det, self.anchor)
            history.append(anchor_point)

            enriched["path_deviation"] = round(self._compute_deviation(history), 4)
            self.outputData.append(enriched)

        return build_response(context=self)


if __name__ == "__main__":
    Executor(sys.argv[1]).run()
