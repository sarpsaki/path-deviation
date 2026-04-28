from pydantic import Field
from typing import Any, Optional, Union, Literal
from sdks.novavision.src.base.model import (
    Package, Image, Inputs, Configs, Outputs, Response, Request,
    Output, Input, Config
)


class AnchorCenter(Config):
    name: Literal["CENTER"] = "CENTER"
    value: Literal["CENTER"] = "CENTER"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Center"
        json_schema_extra = {"shortDescription": "Bounding box merkez noktası"}


class AnchorBottomCenter(Config):
    name: Literal["BOTTOM_CENTER"] = "BOTTOM_CENTER"
    value: Literal["BOTTOM_CENTER"] = "BOTTOM_CENTER"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Bottom Center"
        json_schema_extra = {"shortDescription": "Bounding box alt-merkez noktası"}


class AnchorTopCenter(Config):
    name: Literal["TOP_CENTER"] = "TOP_CENTER"
    value: Literal["TOP_CENTER"] = "TOP_CENTER"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Top Center"
        json_schema_extra = {"shortDescription": "Bounding box üst-merkez noktası"}


class AnchorCenterLeft(Config):
    name: Literal["CENTER_LEFT"] = "CENTER_LEFT"
    value: Literal["CENTER_LEFT"] = "CENTER_LEFT"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Center Left"
        json_schema_extra = {"shortDescription": "Bounding box sol-merkez noktası"}


class AnchorCenterRight(Config):
    name: Literal["CENTER_RIGHT"] = "CENTER_RIGHT"
    value: Literal["CENTER_RIGHT"] = "CENTER_RIGHT"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Center Right"
        json_schema_extra = {"shortDescription": "Bounding box sağ-merkez noktası"}


class ConfigTriggeringAnchor(Config):
    name: Literal["configTriggeringAnchor"] = "configTriggeringAnchor"
    value: Union[
        AnchorCenter,
        AnchorBottomCenter,
        AnchorTopCenter,
        AnchorCenterLeft,
        AnchorCenterRight,
    ]
    type: Literal["object"] = "object"
    field: Literal["dropdownlist"] = "dropdownlist"

    class Config:
        title = "Triggering Anchor"
        json_schema_extra = {"shortDescription": "Nesnenin yolunu hesaplamak için bounding box üzerindeki referans nokta."}


class ConfigReferencePath(Config):
    name: Literal["configReferencePath"] = "configReferencePath"
    value: str = Field(default="[[0,0],[100,100]]")
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "Reference Path (JSON)"
        json_schema_extra = {"shortDescription": "Beklenen referans yol. En az 2 nokta içeren JSON dizisi. Örnek: [[100,200],[200,300],[300,400]]"}


class InputImage(Input):
    name: Literal["inputImage"] = "inputImage"
    value: Union[Image, Any]
    type: Literal["object"] = "object"

    class Config:
        title = "Input Image"
        json_schema_extra = {"shortDescription": "Video metadata'sı gömülü görüntü. Birden fazla video akışı için state ayrımı sağlar."}


class InputDetections(Input):
    name: Literal["inputDetections"] = "inputDetections"
    value: Optional[Any] = None
    type: Literal["list"] = "list"

    class Config:
        title = "Input Detections"
        json_schema_extra = {"shortDescription": "Tracker bloğundan gelen, tracker_id bilgisi içeren nesne tespitleri."}


class OutputDetections(Output):
    name: Literal["outputDetections"] = "outputDetections"
    value: Optional[Any] = None
    type: Literal["list"] = "list"

    class Config:
        title = "Output Detections"
        json_schema_extra = {"shortDescription": "Her tespit için referans yoldan sapma miktarını (Fréchet mesafesi, piksel) içeren güncellenmiş liste."}


class PathDeviationInputs(Inputs):
    inputImage: InputImage
    inputDetections: InputDetections


class PathDeviationConfigs(Configs):
    configTriggeringAnchor: ConfigTriggeringAnchor
    configReferencePath: ConfigReferencePath


class PathDeviationOutputs(Outputs):
    outputDetections: OutputDetections


class PathDeviationRequest(Request):
    inputs: Optional[PathDeviationInputs] = None
    configs: PathDeviationConfigs

    class Config:
        json_schema_extra = {"target": "configs"}


class PathDeviationResponse(Response):
    outputs: PathDeviationOutputs


class PathDeviationExecutor(Config):
    name: Literal["PathDeviation"] = "PathDeviation"
    value: Union[PathDeviationRequest, PathDeviationResponse]
    type: Literal["object"] = "object"
    field: Literal["option"] = "option"

    class Config:
        title = "Path Deviation"
        json_schema_extra = {
            "shortDescription": "Takip edilen nesnelerin gerçek yolunu referans yolla karşılaştırarak Fréchet mesafesini hesaplar.",
            "target": {"value": 0},
        }


class ConfigExecutor(Config):
    name: Literal["ConfigExecutor"] = "ConfigExecutor"
    value: Union[PathDeviationExecutor]
    type: Literal["executor"] = "executor"
    field: Literal["dependentDropdownlist"] = "dependentDropdownlist"

    class Config:
        title = "Algorithm"
        json_schema_extra = {
            "shortDescription": "Çalıştırılacak analitik algoritmayı seçin.",
            "target": "value",
        }


class PackageConfigs(Configs):
    executor: ConfigExecutor


class PackageModel(Package):
    configs: PackageConfigs
    type: Literal["capsule"] = "capsule"
    name: Literal["PathDeviation"] = "PathDeviation"
    uID: str = "7654321"

    class Config:
        json_schema_extra = {"shortDescription": "Takip edilen nesnelerin önceden tanımlanmış bir referans yoldan ne kadar saptığını Fréchet mesafesiyle ölçen kapsül."}