from pydantic import Field, validator
from typing import List, Optional, Union, Literal
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


class AnchorBottomCenter(Config):
    name: Literal["BOTTOM_CENTER"] = "BOTTOM_CENTER"
    value: Literal["BOTTOM_CENTER"] = "BOTTOM_CENTER"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Bottom Center"


class AnchorTopCenter(Config):
    name: Literal["TOP_CENTER"] = "TOP_CENTER"
    value: Literal["TOP_CENTER"] = "TOP_CENTER"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Top Center"


class AnchorCenterLeft(Config):
    name: Literal["CENTER_LEFT"] = "CENTER_LEFT"
    value: Literal["CENTER_LEFT"] = "CENTER_LEFT"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Center Left"


class AnchorCenterRight(Config):
    name: Literal["CENTER_RIGHT"] = "CENTER_RIGHT"
    value: Literal["CENTER_RIGHT"] = "CENTER_RIGHT"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Center Right"


class ConfigTriggeringAnchor(Config):
    """
    Select the anchor point on the bounding box used to track object position across frames.
    The selected point's coordinates are accumulated to build the trajectory that is compared
    against the reference path using Fréchet distance. CENTER is suitable for most use cases.
    """
    name: Literal["ConfigTriggeringAnchor"] = "ConfigTriggeringAnchor"
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
    """
    Define the expected reference path as a JSON array of at least 2 [x, y] coordinate pairs.
    The Fréchet distance between each tracked object's trajectory and this path measures deviation.
    Points must be ordered along the expected direction of travel.
    Example: [[100,200],[200,300],[300,400]]
    """
    name: Literal["ConfigReferencePath"] = "ConfigReferencePath"
    value: str = Field(default="[[0,0],[100,100]]")
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"
    placeHolder: Literal["[[x1,y1],[x2,y2],...]"] = "[[x1,y1],[x2,y2],...]"

    class Config:
        title = "Reference Path (JSON)"
        json_schema_extra = {"shortDescription": "Beklenen referans yol. En az 2 nokta içeren JSON dizisi: [[100,200],[200,300]]"}


class InputImage(Input):
    name: Literal["inputImage"] = "inputImage"
    value: Union[List[Image], Image]
    type: str = "object"

    @validator("type", pre=True, always=True)
    def set_type_based_on_value(cls, value, values):
        value = values.get('value')
        if isinstance(value, Image):
            return "object"
        elif isinstance(value, list):
            return "list"

    class Config:
        title = "Input Image"


class InputDetections(Input):
    name: Literal["inputDetections"] = "inputDetections"
    value: Union[dict, list]
    type: Literal["list"] = "list"

    class Config:
        title = "Input Detections"


class OutputDetections(Output):
    name: Literal["outputDetections"] = "outputDetections"
    value: Union[dict, list]
    type: Literal["list"] = "list"

    class Config:
        title = "Output Detections"


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
