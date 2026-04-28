import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../"))

from sdks.novavision.src.base.capsule import Capsule
from sdks.novavision.src.helper.executor import Executor
from capsules.PathDeviation.src.utils.response import build_response
from capsules.PathDeviation.src.models.PackageModel import PackageModel
from capsules.PathDeviation.src.utils.frechet import frechet_distance, get_anchor_point

# { video_id: { tracker_id: [(x, y), ...] } }
_PATH_STORE: dict = {}


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
        return {}

    @staticmethod
    def _extract_video_id(image) -> str:
        try:
            return str(image.video_metadata.video_identifier)
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

    def _get_or_create_history(self, tracker_id: str) -> list:
        if self.video_id not in _PATH_STORE:
            _PATH_STORE[self.video_id] = {}
        if tracker_id not in _PATH_STORE[self.video_id]:
            _PATH_STORE[self.video_id][tracker_id] = []
        return _PATH_STORE[self.video_id][tracker_id]

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
            tracker_id = det.get("tracker_id") or det.get("trackerId")

            if tracker_id is None:
                det["path_deviation"] = None
                self.outputData.append(det)
                continue

            tracker_id   = str(tracker_id)
            history      = self._get_or_create_history(tracker_id)
            anchor_point = get_anchor_point(det, self.anchor)
            history.append(anchor_point)

            enriched = dict(det)
            enriched["path_deviation"] = round(self._compute_deviation(history), 4)
            self.outputData.append(enriched)

        return build_response(context=self)


if __name__ == "__main__":
    Executor(sys.argv[1]).run()