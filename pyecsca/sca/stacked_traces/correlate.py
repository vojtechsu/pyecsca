import numpy as np
import numpy.typing as npt
from numba import cuda
from numba.cuda.cudadrv.devicearray import DeviceNDArray
from math import sqrt
from typing import List, Optional, Union
from .combine import InputType, GPUTraceManager
from .stacked_traces import StackedTraces
from ..trace.trace import CombinedTrace


def gpu_pearson_corr(intermediate_values: npt.NDArray[np.number],
                     stacked_traces: Optional[StackedTraces] = None,
                     trace_manager: Optional[GPUTraceManager] = None,
                     **tm_kwargs) -> Union[CombinedTrace, List[CombinedTrace]]:
    if (stacked_traces is None) == (trace_manager is None):
        raise ValueError("Either samples or trace manager must be given.")

    if trace_manager is None:
        assert stacked_traces is not None
        trace_manager = GPUTraceManager(stacked_traces, **tm_kwargs)

    if (len(intermediate_values.shape) != 1
        or (intermediate_values.shape[0]
            != trace_manager.traces_shape[0])):
        raise ValueError("Intermediate values have to be a vector "
                         "as long as trace_count")

    intermed_sum: np.number = np.sum(intermediate_values)
    intermed_sq_sum: np.number = np.sum(np.square(intermediate_values))
    inputs: List[InputType] = [intermediate_values,
                               np.array([intermed_sum]),
                               np.array([intermed_sq_sum])]

    return trace_manager.run(
        _gpu_pearson_corr,
        inputs
    )


@cuda.jit(cache=True)
def _gpu_pearson_corr(samples: DeviceNDArray,
                      intermediate_values: DeviceNDArray,
                      intermed_sum: DeviceNDArray,
                      intermed_sq_sum: DeviceNDArray,
                      result: DeviceNDArray):
    """
    Calculates the Pearson correlation coefficient between the given samples and intermediate values using GPU acceleration.

    :param samples: A 2D array of shape (n, m) containing the samples.
    :type samples: npt.NDArray[np.number]
    :param intermediate_values: A 1D array of shape (n,) containing the intermediate values.
    :type intermediate_values: npt.NDArray[np.number]
    :param intermed_sum: A 1D array of shape (1,) containing the precomputed sum of the intermediate values.
    :type intermed_sum: npt.NDArray[np.number]
    :param intermed_sq_sum: A 1D array of shape (1,) containing the precomputed sum of the squares of the intermediate values.
    :param result: A 1D array of shape (m,) to store the resulting correlation coefficients.
    :type result: cuda.devicearray.DeviceNDArray
    """
    col: int = cuda.grid(1)  # type: ignore

    if col >= samples.shape[1]:  # type: ignore
        return

    n = samples.shape[0]
    samples_sum = 0.
    samples_sq_sum = 0.
    product_sum = 0.

    for row in range(n):
        samples_sum += samples[row, col]
        samples_sq_sum += samples[row, col] ** 2
        product_sum += samples[row, col] * intermediate_values[row]

    numerator = float(n) * product_sum - samples_sum * intermed_sum[0]
    denom_samp = sqrt(float(n) * samples_sq_sum - samples_sum ** 2)
    denom_int = sqrt(float(n) * intermed_sq_sum[0] - intermed_sum[0] ** 2)
    denominator = denom_samp * denom_int

    result[col] = numerator / denominator
