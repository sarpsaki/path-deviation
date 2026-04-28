from sdks.novavision.src.helper.package import PackageHelper
from capsules.PathDeviation.src.models.PackageModel import (
    PackageModel,
    PackageConfigs,
    ConfigExecutor,
    PathDeviationExecutor,
    PathDeviationOutputs,
    PathDeviationResponse,
    OutputDetections,
)


def build_response(context) -> dict:
    outputDetections = OutputDetections(value=context.outputData)
    outputs          = PathDeviationOutputs(outputDetections=outputDetections)
    packageResponse  = PathDeviationResponse(outputs=outputs)
    packageExecutor  = PathDeviationExecutor(value=packageResponse)
    executor         = ConfigExecutor(value=packageExecutor)
    packageConfigs   = PackageConfigs(executor=executor)
    package          = PackageHelper(packageModel=PackageModel, packageConfigs=packageConfigs)
    return package.build_model(context)