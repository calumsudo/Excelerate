import sys
import threading
from typing import Any
from collections.abc import Sequence

import numpy as np
import numpy.typing as npt
from numpy.random._generator import Generator
from numpy.random._mt19937 import MT19937
from numpy.random._pcg64 import PCG64
from numpy.random._sfc64 import SFC64
from numpy.random._philox import Philox
from numpy.random.bit_generator import SeedSequence, SeedlessSeedSequence

if sys.version_info >= (3, 11):
    from typing import assert_type
else:
    from typing_extensions import assert_type

def_rng = np.random.default_rng()
seed_seq = np.random.SeedSequence()
mt19937 = np.random.MT19937()
pcg64 = np.random.PCG64()
sfc64 = np.random.SFC64()
philox = np.random.Philox()
seedless_seq = SeedlessSeedSequence()

assert_type(def_rng, Generator)
assert_type(mt19937, MT19937)
assert_type(pcg64, PCG64)
assert_type(sfc64, SFC64)
assert_type(philox, Philox)
assert_type(seed_seq, SeedSequence)
assert_type(seedless_seq, SeedlessSeedSequence)

mt19937_jumped = mt19937.jumped()
mt19937_jumped3 = mt19937.jumped(3)
mt19937_raw = mt19937.random_raw()
mt19937_raw_arr = mt19937.random_raw(5)

assert_type(mt19937_jumped, MT19937)
assert_type(mt19937_jumped3, MT19937)
assert_type(mt19937_raw, int)
assert_type(mt19937_raw_arr, npt.NDArray[np.uint64])
assert_type(mt19937.lock, threading.Lock)

pcg64_jumped = pcg64.jumped()
pcg64_jumped3 = pcg64.jumped(3)
pcg64_adv = pcg64.advance(3)
pcg64_raw = pcg64.random_raw()
pcg64_raw_arr = pcg64.random_raw(5)

assert_type(pcg64_jumped, PCG64)
assert_type(pcg64_jumped3, PCG64)
assert_type(pcg64_adv, PCG64)
assert_type(pcg64_raw, int)
assert_type(pcg64_raw_arr, npt.NDArray[np.uint64])
assert_type(pcg64.lock, threading.Lock)

philox_jumped = philox.jumped()
philox_jumped3 = philox.jumped(3)
philox_adv = philox.advance(3)
philox_raw = philox.random_raw()
philox_raw_arr = philox.random_raw(5)

assert_type(philox_jumped, Philox)
assert_type(philox_jumped3, Philox)
assert_type(philox_adv, Philox)
assert_type(philox_raw, int)
assert_type(philox_raw_arr, npt.NDArray[np.uint64])
assert_type(philox.lock, threading.Lock)

sfc64_raw = sfc64.random_raw()
sfc64_raw_arr = sfc64.random_raw(5)

assert_type(sfc64_raw, int)
assert_type(sfc64_raw_arr, npt.NDArray[np.uint64])
assert_type(sfc64.lock, threading.Lock)

assert_type(seed_seq.pool, npt.NDArray[np.uint32])
assert_type(seed_seq.entropy, None | int | Sequence[int])
assert_type(seed_seq.spawn(1), list[np.random.SeedSequence])
assert_type(seed_seq.generate_state(8, "uint32"), npt.NDArray[np.uint32 | np.uint64])
assert_type(seed_seq.generate_state(8, "uint64"), npt.NDArray[np.uint32 | np.uint64])

def_gen: np.random.Generator = np.random.default_rng()

D_arr_0p1: npt.NDArray[np.float64] = np.array([0.1])
D_arr_0p5: npt.NDArray[np.float64] = np.array([0.5])
D_arr_0p9: npt.NDArray[np.float64] = np.array([0.9])
D_arr_1p5: npt.NDArray[np.float64] = np.array([1.5])
I_arr_10: np.ndarray[Any, np.dtype[np.int_]] = np.array([10], dtype=np.int_)
I_arr_20: np.ndarray[Any, np.dtype[np.int_]] = np.array([20], dtype=np.int_)
D_arr_like_0p1: list[float] = [0.1]
D_arr_like_0p5: list[float] = [0.5]
D_arr_like_0p9: list[float] = [0.9]
D_arr_like_1p5: list[float] = [1.5]
I_arr_like_10: list[int] = [10]
I_arr_like_20: list[int] = [20]
D_2D_like: list[list[float]] = [[1, 2], [2, 3], [3, 4], [4, 5.1]]
D_2D: npt.NDArray[np.float64] = np.array(D_2D_like)
S_out: npt.NDArray[np.float32] = np.empty(1, dtype=np.float32)
D_out: npt.NDArray[np.float64] = np.empty(1)

assert_type(def_gen.standard_normal(), float)
assert_type(def_gen.standard_normal(dtype=np.float32), float)
assert_type(def_gen.standard_normal(dtype="float32"), float)
assert_type(def_gen.standard_normal(dtype="double"), float)
assert_type(def_gen.standard_normal(dtype=np.float64), float)
assert_type(def_gen.standard_normal(size=None), float)
assert_type(def_gen.standard_normal(size=1), npt.NDArray[np.float64])
assert_type(def_gen.standard_normal(size=1, dtype=np.float32), npt.NDArray[np.float32])
assert_type(def_gen.standard_normal(size=1, dtype="f4"), npt.NDArray[np.float32])
assert_type(
    def_gen.standard_normal(size=1, dtype="float32", out=S_out), npt.NDArray[np.float32]
)
assert_type(
    def_gen.standard_normal(dtype=np.float32, out=S_out), npt.NDArray[np.float32]
)
assert_type(def_gen.standard_normal(size=1, dtype=np.float64), npt.NDArray[np.float64])
assert_type(def_gen.standard_normal(size=1, dtype="float64"), npt.NDArray[np.float64])
assert_type(def_gen.standard_normal(size=1, dtype="f8"), npt.NDArray[np.float64])
assert_type(def_gen.standard_normal(out=D_out), npt.NDArray[np.float64])
assert_type(def_gen.standard_normal(size=1, dtype="float64"), npt.NDArray[np.float64])
assert_type(
    def_gen.standard_normal(size=1, dtype="float64", out=D_out), npt.NDArray[np.float64]
)

assert_type(def_gen.random(), float)
assert_type(def_gen.random(dtype=np.float32), float)
assert_type(def_gen.random(dtype="float32"), float)
assert_type(def_gen.random(dtype="double"), float)
assert_type(def_gen.random(dtype=np.float64), float)
assert_type(def_gen.random(size=None), float)
assert_type(def_gen.random(size=1), npt.NDArray[np.float64])
assert_type(def_gen.random(size=1, dtype=np.float32), npt.NDArray[np.float32])
assert_type(def_gen.random(size=1, dtype="f4"), npt.NDArray[np.float32])
assert_type(def_gen.random(size=1, dtype="float32", out=S_out), npt.NDArray[np.float32])
assert_type(def_gen.random(dtype=np.float32, out=S_out), npt.NDArray[np.float32])
assert_type(def_gen.random(size=1, dtype=np.float64), npt.NDArray[np.float64])
assert_type(def_gen.random(size=1, dtype="float64"), npt.NDArray[np.float64])
assert_type(def_gen.random(size=1, dtype="f8"), npt.NDArray[np.float64])
assert_type(def_gen.random(out=D_out), npt.NDArray[np.float64])
assert_type(def_gen.random(size=1, dtype="float64"), npt.NDArray[np.float64])
assert_type(def_gen.random(size=1, dtype="float64", out=D_out), npt.NDArray[np.float64])

assert_type(def_gen.standard_cauchy(), float)
assert_type(def_gen.standard_cauchy(size=None), float)
assert_type(def_gen.standard_cauchy(size=1), npt.NDArray[np.float64])

assert_type(def_gen.standard_exponential(), float)
assert_type(def_gen.standard_exponential(method="inv"), float)
assert_type(def_gen.standard_exponential(dtype=np.float32), float)
assert_type(def_gen.standard_exponential(dtype="float32"), float)
assert_type(def_gen.standard_exponential(dtype="double"), float)
assert_type(def_gen.standard_exponential(dtype=np.float64), float)
assert_type(def_gen.standard_exponential(size=None), float)
assert_type(def_gen.standard_exponential(size=None, method="inv"), float)
assert_type(def_gen.standard_exponential(size=1, method="inv"), npt.NDArray[np.float64])
assert_type(
    def_gen.standard_exponential(size=1, dtype=np.float32), npt.NDArray[np.float32]
)
assert_type(
    def_gen.standard_exponential(size=1, dtype="f4", method="inv"),
    npt.NDArray[np.float32],
)
assert_type(
    def_gen.standard_exponential(size=1, dtype="float32", out=S_out),
    npt.NDArray[np.float32],
)
assert_type(
    def_gen.standard_exponential(dtype=np.float32, out=S_out), npt.NDArray[np.float32]
)
assert_type(
    def_gen.standard_exponential(size=1, dtype=np.float64, method="inv"),
    npt.NDArray[np.float64],
)
assert_type(
    def_gen.standard_exponential(size=1, dtype="float64"), npt.NDArray[np.float64]
)
assert_type(def_gen.standard_exponential(size=1, dtype="f8"), npt.NDArray[np.float64])
assert_type(def_gen.standard_exponential(out=D_out), npt.NDArray[np.float64])
assert_type(
    def_gen.standard_exponential(size=1, dtype="float64"), npt.NDArray[np.float64]
)
assert_type(
    def_gen.standard_exponential(size=1, dtype="float64", out=D_out),
    npt.NDArray[np.float64],
)

assert_type(def_gen.zipf(1.5), int)
assert_type(def_gen.zipf(1.5, size=None), int)
assert_type(def_gen.zipf(1.5, size=1), npt.NDArray[np.int64])
assert_type(def_gen.zipf(D_arr_1p5), npt.NDArray[np.int64])
assert_type(def_gen.zipf(D_arr_1p5, size=1), npt.NDArray[np.int64])
assert_type(def_gen.zipf(D_arr_like_1p5), npt.NDArray[np.int64])
assert_type(def_gen.zipf(D_arr_like_1p5, size=1), npt.NDArray[np.int64])

assert_type(def_gen.weibull(0.5), float)
assert_type(def_gen.weibull(0.5, size=None), float)
assert_type(def_gen.weibull(0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.weibull(D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.weibull(D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.weibull(D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.weibull(D_arr_like_0p5, size=1), npt.NDArray[np.float64])

assert_type(def_gen.standard_t(0.5), float)
assert_type(def_gen.standard_t(0.5, size=None), float)
assert_type(def_gen.standard_t(0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.standard_t(D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.standard_t(D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.standard_t(D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.standard_t(D_arr_like_0p5, size=1), npt.NDArray[np.float64])

assert_type(def_gen.poisson(0.5), int)
assert_type(def_gen.poisson(0.5, size=None), int)
assert_type(def_gen.poisson(0.5, size=1), npt.NDArray[np.int64])
assert_type(def_gen.poisson(D_arr_0p5), npt.NDArray[np.int64])
assert_type(def_gen.poisson(D_arr_0p5, size=1), npt.NDArray[np.int64])
assert_type(def_gen.poisson(D_arr_like_0p5), npt.NDArray[np.int64])
assert_type(def_gen.poisson(D_arr_like_0p5, size=1), npt.NDArray[np.int64])

assert_type(def_gen.power(0.5), float)
assert_type(def_gen.power(0.5, size=None), float)
assert_type(def_gen.power(0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.power(D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.power(D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.power(D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.power(D_arr_like_0p5, size=1), npt.NDArray[np.float64])

assert_type(def_gen.pareto(0.5), float)
assert_type(def_gen.pareto(0.5, size=None), float)
assert_type(def_gen.pareto(0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.pareto(D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.pareto(D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.pareto(D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.pareto(D_arr_like_0p5, size=1), npt.NDArray[np.float64])

assert_type(def_gen.chisquare(0.5), float)
assert_type(def_gen.chisquare(0.5, size=None), float)
assert_type(def_gen.chisquare(0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.chisquare(D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.chisquare(D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.chisquare(D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.chisquare(D_arr_like_0p5, size=1), npt.NDArray[np.float64])

assert_type(def_gen.exponential(0.5), float)
assert_type(def_gen.exponential(0.5, size=None), float)
assert_type(def_gen.exponential(0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.exponential(D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.exponential(D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.exponential(D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.exponential(D_arr_like_0p5, size=1), npt.NDArray[np.float64])

assert_type(def_gen.geometric(0.5), int)
assert_type(def_gen.geometric(0.5, size=None), int)
assert_type(def_gen.geometric(0.5, size=1), npt.NDArray[np.int64])
assert_type(def_gen.geometric(D_arr_0p5), npt.NDArray[np.int64])
assert_type(def_gen.geometric(D_arr_0p5, size=1), npt.NDArray[np.int64])
assert_type(def_gen.geometric(D_arr_like_0p5), npt.NDArray[np.int64])
assert_type(def_gen.geometric(D_arr_like_0p5, size=1), npt.NDArray[np.int64])

assert_type(def_gen.logseries(0.5), int)
assert_type(def_gen.logseries(0.5, size=None), int)
assert_type(def_gen.logseries(0.5, size=1), npt.NDArray[np.int64])
assert_type(def_gen.logseries(D_arr_0p5), npt.NDArray[np.int64])
assert_type(def_gen.logseries(D_arr_0p5, size=1), npt.NDArray[np.int64])
assert_type(def_gen.logseries(D_arr_like_0p5), npt.NDArray[np.int64])
assert_type(def_gen.logseries(D_arr_like_0p5, size=1), npt.NDArray[np.int64])

assert_type(def_gen.rayleigh(0.5), float)
assert_type(def_gen.rayleigh(0.5, size=None), float)
assert_type(def_gen.rayleigh(0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.rayleigh(D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.rayleigh(D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.rayleigh(D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.rayleigh(D_arr_like_0p5, size=1), npt.NDArray[np.float64])

assert_type(def_gen.standard_gamma(0.5), float)
assert_type(def_gen.standard_gamma(0.5, size=None), float)
assert_type(def_gen.standard_gamma(0.5, dtype="float32"), float)
assert_type(def_gen.standard_gamma(0.5, size=None, dtype="float32"), float)
assert_type(def_gen.standard_gamma(0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.standard_gamma(D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.standard_gamma(D_arr_0p5, dtype="f4"), npt.NDArray[np.float32])
assert_type(
    def_gen.standard_gamma(0.5, size=1, dtype="float32", out=S_out),
    npt.NDArray[np.float32],
)
assert_type(
    def_gen.standard_gamma(D_arr_0p5, dtype=np.float32, out=S_out),
    npt.NDArray[np.float32],
)
assert_type(def_gen.standard_gamma(D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.standard_gamma(D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.standard_gamma(D_arr_like_0p5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.standard_gamma(0.5, out=D_out), npt.NDArray[np.float64])
assert_type(def_gen.standard_gamma(D_arr_like_0p5, out=D_out), npt.NDArray[np.float64])
assert_type(def_gen.standard_gamma(D_arr_like_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    def_gen.standard_gamma(D_arr_like_0p5, size=1, out=D_out, dtype=np.float64),
    npt.NDArray[np.float64],
)

assert_type(def_gen.vonmises(0.5, 0.5), float)
assert_type(def_gen.vonmises(0.5, 0.5, size=None), float)
assert_type(def_gen.vonmises(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.vonmises(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.vonmises(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.vonmises(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.vonmises(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.vonmises(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.vonmises(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.vonmises(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.vonmises(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.vonmises(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    def_gen.vonmises(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64]
)

assert_type(def_gen.wald(0.5, 0.5), float)
assert_type(def_gen.wald(0.5, 0.5, size=None), float)
assert_type(def_gen.wald(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.wald(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.wald(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.wald(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.wald(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.wald(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.wald(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.wald(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.wald(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.wald(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    def_gen.wald(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64]
)

assert_type(def_gen.uniform(0.5, 0.5), float)
assert_type(def_gen.uniform(0.5, 0.5, size=None), float)
assert_type(def_gen.uniform(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.uniform(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.uniform(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.uniform(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.uniform(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.uniform(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.uniform(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.uniform(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.uniform(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.uniform(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    def_gen.uniform(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64]
)

assert_type(def_gen.beta(0.5, 0.5), float)
assert_type(def_gen.beta(0.5, 0.5, size=None), float)
assert_type(def_gen.beta(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.beta(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.beta(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.beta(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.beta(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.beta(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.beta(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.beta(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.beta(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.beta(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    def_gen.beta(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64]
)

assert_type(def_gen.f(0.5, 0.5), float)
assert_type(def_gen.f(0.5, 0.5, size=None), float)
assert_type(def_gen.f(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.f(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.f(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.f(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.f(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.f(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.f(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.f(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.f(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.f(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.f(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64])

assert_type(def_gen.gamma(0.5, 0.5), float)
assert_type(def_gen.gamma(0.5, 0.5, size=None), float)
assert_type(def_gen.gamma(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.gamma(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.gamma(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.gamma(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.gamma(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.gamma(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.gamma(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.gamma(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.gamma(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.gamma(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    def_gen.gamma(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64]
)

assert_type(def_gen.gumbel(0.5, 0.5), float)
assert_type(def_gen.gumbel(0.5, 0.5, size=None), float)
assert_type(def_gen.gumbel(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.gumbel(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.gumbel(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.gumbel(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.gumbel(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.gumbel(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.gumbel(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.gumbel(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.gumbel(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.gumbel(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    def_gen.gumbel(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64]
)

assert_type(def_gen.laplace(0.5, 0.5), float)
assert_type(def_gen.laplace(0.5, 0.5, size=None), float)
assert_type(def_gen.laplace(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.laplace(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.laplace(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.laplace(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.laplace(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.laplace(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.laplace(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.laplace(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.laplace(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.laplace(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    def_gen.laplace(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64]
)

assert_type(def_gen.logistic(0.5, 0.5), float)
assert_type(def_gen.logistic(0.5, 0.5, size=None), float)
assert_type(def_gen.logistic(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.logistic(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.logistic(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.logistic(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.logistic(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.logistic(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.logistic(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.logistic(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.logistic(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.logistic(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    def_gen.logistic(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64]
)

assert_type(def_gen.lognormal(0.5, 0.5), float)
assert_type(def_gen.lognormal(0.5, 0.5, size=None), float)
assert_type(def_gen.lognormal(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.lognormal(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.lognormal(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.lognormal(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.lognormal(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.lognormal(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.lognormal(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.lognormal(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.lognormal(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.lognormal(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    def_gen.lognormal(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64]
)

assert_type(def_gen.noncentral_chisquare(0.5, 0.5), float)
assert_type(def_gen.noncentral_chisquare(0.5, 0.5, size=None), float)
assert_type(def_gen.noncentral_chisquare(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.noncentral_chisquare(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.noncentral_chisquare(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(
    def_gen.noncentral_chisquare(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64]
)
assert_type(
    def_gen.noncentral_chisquare(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64]
)
assert_type(def_gen.noncentral_chisquare(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.noncentral_chisquare(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.noncentral_chisquare(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(
    def_gen.noncentral_chisquare(D_arr_like_0p5, D_arr_like_0p5),
    npt.NDArray[np.float64],
)
assert_type(
    def_gen.noncentral_chisquare(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64]
)
assert_type(
    def_gen.noncentral_chisquare(D_arr_like_0p5, D_arr_like_0p5, size=1),
    npt.NDArray[np.float64],
)

assert_type(def_gen.normal(0.5, 0.5), float)
assert_type(def_gen.normal(0.5, 0.5, size=None), float)
assert_type(def_gen.normal(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.normal(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.normal(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.normal(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.normal(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(def_gen.normal(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(def_gen.normal(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.normal(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(def_gen.normal(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(def_gen.normal(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    def_gen.normal(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64]
)

assert_type(def_gen.triangular(0.1, 0.5, 0.9), float)
assert_type(def_gen.triangular(0.1, 0.5, 0.9, size=None), float)
assert_type(def_gen.triangular(0.1, 0.5, 0.9, size=1), npt.NDArray[np.float64])
assert_type(def_gen.triangular(D_arr_0p1, 0.5, 0.9), npt.NDArray[np.float64])
assert_type(def_gen.triangular(0.1, D_arr_0p5, 0.9), npt.NDArray[np.float64])
assert_type(
    def_gen.triangular(D_arr_0p1, 0.5, D_arr_like_0p9, size=1), npt.NDArray[np.float64]
)
assert_type(def_gen.triangular(0.1, D_arr_0p5, 0.9, size=1), npt.NDArray[np.float64])
assert_type(def_gen.triangular(D_arr_like_0p1, 0.5, D_arr_0p9), npt.NDArray[np.float64])
assert_type(def_gen.triangular(0.5, D_arr_like_0p5, 0.9), npt.NDArray[np.float64])
assert_type(def_gen.triangular(D_arr_0p1, D_arr_0p5, 0.9), npt.NDArray[np.float64])
assert_type(
    def_gen.triangular(D_arr_like_0p1, D_arr_like_0p5, 0.9), npt.NDArray[np.float64]
)
assert_type(
    def_gen.triangular(D_arr_0p1, D_arr_0p5, D_arr_0p9, size=1), npt.NDArray[np.float64]
)
assert_type(
    def_gen.triangular(D_arr_like_0p1, D_arr_like_0p5, D_arr_like_0p9, size=1),
    npt.NDArray[np.float64],
)

assert_type(def_gen.noncentral_f(0.1, 0.5, 0.9), float)
assert_type(def_gen.noncentral_f(0.1, 0.5, 0.9, size=None), float)
assert_type(def_gen.noncentral_f(0.1, 0.5, 0.9, size=1), npt.NDArray[np.float64])
assert_type(def_gen.noncentral_f(D_arr_0p1, 0.5, 0.9), npt.NDArray[np.float64])
assert_type(def_gen.noncentral_f(0.1, D_arr_0p5, 0.9), npt.NDArray[np.float64])
assert_type(
    def_gen.noncentral_f(D_arr_0p1, 0.5, D_arr_like_0p9, size=1),
    npt.NDArray[np.float64],
)
assert_type(def_gen.noncentral_f(0.1, D_arr_0p5, 0.9, size=1), npt.NDArray[np.float64])
assert_type(
    def_gen.noncentral_f(D_arr_like_0p1, 0.5, D_arr_0p9), npt.NDArray[np.float64]
)
assert_type(def_gen.noncentral_f(0.5, D_arr_like_0p5, 0.9), npt.NDArray[np.float64])
assert_type(def_gen.noncentral_f(D_arr_0p1, D_arr_0p5, 0.9), npt.NDArray[np.float64])
assert_type(
    def_gen.noncentral_f(D_arr_like_0p1, D_arr_like_0p5, 0.9), npt.NDArray[np.float64]
)
assert_type(
    def_gen.noncentral_f(D_arr_0p1, D_arr_0p5, D_arr_0p9, size=1),
    npt.NDArray[np.float64],
)
assert_type(
    def_gen.noncentral_f(D_arr_like_0p1, D_arr_like_0p5, D_arr_like_0p9, size=1),
    npt.NDArray[np.float64],
)

assert_type(def_gen.binomial(10, 0.5), int)
assert_type(def_gen.binomial(10, 0.5, size=None), int)
assert_type(def_gen.binomial(10, 0.5, size=1), npt.NDArray[np.int64])
assert_type(def_gen.binomial(I_arr_10, 0.5), npt.NDArray[np.int64])
assert_type(def_gen.binomial(10, D_arr_0p5), npt.NDArray[np.int64])
assert_type(def_gen.binomial(I_arr_10, 0.5, size=1), npt.NDArray[np.int64])
assert_type(def_gen.binomial(10, D_arr_0p5, size=1), npt.NDArray[np.int64])
assert_type(def_gen.binomial(I_arr_like_10, 0.5), npt.NDArray[np.int64])
assert_type(def_gen.binomial(10, D_arr_like_0p5), npt.NDArray[np.int64])
assert_type(def_gen.binomial(I_arr_10, D_arr_0p5), npt.NDArray[np.int64])
assert_type(def_gen.binomial(I_arr_like_10, D_arr_like_0p5), npt.NDArray[np.int64])
assert_type(def_gen.binomial(I_arr_10, D_arr_0p5, size=1), npt.NDArray[np.int64])
assert_type(
    def_gen.binomial(I_arr_like_10, D_arr_like_0p5, size=1), npt.NDArray[np.int64]
)

assert_type(def_gen.negative_binomial(10, 0.5), int)
assert_type(def_gen.negative_binomial(10, 0.5, size=None), int)
assert_type(def_gen.negative_binomial(10, 0.5, size=1), npt.NDArray[np.int64])
assert_type(def_gen.negative_binomial(I_arr_10, 0.5), npt.NDArray[np.int64])
assert_type(def_gen.negative_binomial(10, D_arr_0p5), npt.NDArray[np.int64])
assert_type(def_gen.negative_binomial(I_arr_10, 0.5, size=1), npt.NDArray[np.int64])
assert_type(def_gen.negative_binomial(10, D_arr_0p5, size=1), npt.NDArray[np.int64])
assert_type(def_gen.negative_binomial(I_arr_like_10, 0.5), npt.NDArray[np.int64])
assert_type(def_gen.negative_binomial(10, D_arr_like_0p5), npt.NDArray[np.int64])
assert_type(def_gen.negative_binomial(I_arr_10, D_arr_0p5), npt.NDArray[np.int64])
assert_type(
    def_gen.negative_binomial(I_arr_like_10, D_arr_like_0p5), npt.NDArray[np.int64]
)
assert_type(
    def_gen.negative_binomial(I_arr_10, D_arr_0p5, size=1), npt.NDArray[np.int64]
)
assert_type(
    def_gen.negative_binomial(I_arr_like_10, D_arr_like_0p5, size=1),
    npt.NDArray[np.int64],
)

assert_type(def_gen.hypergeometric(20, 20, 10), int)
assert_type(def_gen.hypergeometric(20, 20, 10, size=None), int)
assert_type(def_gen.hypergeometric(20, 20, 10, size=1), npt.NDArray[np.int64])
assert_type(def_gen.hypergeometric(I_arr_20, 20, 10), npt.NDArray[np.int64])
assert_type(def_gen.hypergeometric(20, I_arr_20, 10), npt.NDArray[np.int64])
assert_type(
    def_gen.hypergeometric(I_arr_20, 20, I_arr_like_10, size=1), npt.NDArray[np.int64]
)
assert_type(def_gen.hypergeometric(20, I_arr_20, 10, size=1), npt.NDArray[np.int64])
assert_type(def_gen.hypergeometric(I_arr_like_20, 20, I_arr_10), npt.NDArray[np.int64])
assert_type(def_gen.hypergeometric(20, I_arr_like_20, 10), npt.NDArray[np.int64])
assert_type(def_gen.hypergeometric(I_arr_20, I_arr_20, 10), npt.NDArray[np.int64])
assert_type(
    def_gen.hypergeometric(I_arr_like_20, I_arr_like_20, 10), npt.NDArray[np.int64]
)
assert_type(
    def_gen.hypergeometric(I_arr_20, I_arr_20, I_arr_10, size=1), npt.NDArray[np.int64]
)
assert_type(
    def_gen.hypergeometric(I_arr_like_20, I_arr_like_20, I_arr_like_10, size=1),
    npt.NDArray[np.int64],
)

I_int64_100: np.ndarray[Any, np.dtype[np.int64]] = np.array([100], dtype=np.int64)

assert_type(def_gen.integers(0, 100), int)
assert_type(def_gen.integers(100), int)
assert_type(def_gen.integers([100]), npt.NDArray[np.int64])
assert_type(def_gen.integers(0, [100]), npt.NDArray[np.int64])

I_bool_low: npt.NDArray[np.bool_] = np.array([0], dtype=np.bool_)
I_bool_low_like: list[int] = [0]
I_bool_high_open: npt.NDArray[np.bool_] = np.array([1], dtype=np.bool_)
I_bool_high_closed: npt.NDArray[np.bool_] = np.array([1], dtype=np.bool_)

assert_type(def_gen.integers(2, dtype=bool), bool)
assert_type(def_gen.integers(0, 2, dtype=bool), bool)
assert_type(def_gen.integers(1, dtype=bool, endpoint=True), bool)
assert_type(def_gen.integers(0, 1, dtype=bool, endpoint=True), bool)
assert_type(
    def_gen.integers(I_bool_low_like, 1, dtype=bool, endpoint=True),
    npt.NDArray[np.bool_],
)
assert_type(def_gen.integers(I_bool_high_open, dtype=bool), npt.NDArray[np.bool_])
assert_type(
    def_gen.integers(I_bool_low, I_bool_high_open, dtype=bool), npt.NDArray[np.bool_]
)
assert_type(def_gen.integers(0, I_bool_high_open, dtype=bool), npt.NDArray[np.bool_])
assert_type(
    def_gen.integers(I_bool_high_closed, dtype=bool, endpoint=True),
    npt.NDArray[np.bool_],
)
assert_type(
    def_gen.integers(I_bool_low, I_bool_high_closed, dtype=bool, endpoint=True),
    npt.NDArray[np.bool_],
)
assert_type(
    def_gen.integers(0, I_bool_high_closed, dtype=bool, endpoint=True),
    npt.NDArray[np.bool_],
)

assert_type(def_gen.integers(2, dtype=np.bool_), bool)
assert_type(def_gen.integers(0, 2, dtype=np.bool_), bool)
assert_type(def_gen.integers(1, dtype=np.bool_, endpoint=True), bool)
assert_type(def_gen.integers(0, 1, dtype=np.bool_, endpoint=True), bool)
assert_type(
    def_gen.integers(I_bool_low_like, 1, dtype=np.bool_, endpoint=True),
    npt.NDArray[np.bool_],
)
assert_type(def_gen.integers(I_bool_high_open, dtype=np.bool_), npt.NDArray[np.bool_])
assert_type(
    def_gen.integers(I_bool_low, I_bool_high_open, dtype=np.bool_),
    npt.NDArray[np.bool_],
)
assert_type(
    def_gen.integers(0, I_bool_high_open, dtype=np.bool_), npt.NDArray[np.bool_]
)
assert_type(
    def_gen.integers(I_bool_high_closed, dtype=np.bool_, endpoint=True),
    npt.NDArray[np.bool_],
)
assert_type(
    def_gen.integers(I_bool_low, I_bool_high_closed, dtype=np.bool_, endpoint=True),
    npt.NDArray[np.bool_],
)
assert_type(
    def_gen.integers(0, I_bool_high_closed, dtype=np.bool_, endpoint=True),
    npt.NDArray[np.bool_],
)

I_u1_low: np.ndarray[Any, np.dtype[np.uint8]] = np.array([0], dtype=np.uint8)
I_u1_low_like: list[int] = [0]
I_u1_high_open: np.ndarray[Any, np.dtype[np.uint8]] = np.array([255], dtype=np.uint8)
I_u1_high_closed: np.ndarray[Any, np.dtype[np.uint8]] = np.array([255], dtype=np.uint8)

assert_type(def_gen.integers(256, dtype="u1"), int)
assert_type(def_gen.integers(0, 256, dtype="u1"), int)
assert_type(def_gen.integers(255, dtype="u1", endpoint=True), int)
assert_type(def_gen.integers(0, 255, dtype="u1", endpoint=True), int)
assert_type(
    def_gen.integers(I_u1_low_like, 255, dtype="u1", endpoint=True),
    npt.NDArray[np.uint8],
)
assert_type(def_gen.integers(I_u1_high_open, dtype="u1"), npt.NDArray[np.uint8])
assert_type(
    def_gen.integers(I_u1_low, I_u1_high_open, dtype="u1"), npt.NDArray[np.uint8]
)
assert_type(def_gen.integers(0, I_u1_high_open, dtype="u1"), npt.NDArray[np.uint8])
assert_type(
    def_gen.integers(I_u1_high_closed, dtype="u1", endpoint=True), npt.NDArray[np.uint8]
)
assert_type(
    def_gen.integers(I_u1_low, I_u1_high_closed, dtype="u1", endpoint=True),
    npt.NDArray[np.uint8],
)
assert_type(
    def_gen.integers(0, I_u1_high_closed, dtype="u1", endpoint=True),
    npt.NDArray[np.uint8],
)

assert_type(def_gen.integers(256, dtype="uint8"), int)
assert_type(def_gen.integers(0, 256, dtype="uint8"), int)
assert_type(def_gen.integers(255, dtype="uint8", endpoint=True), int)
assert_type(def_gen.integers(0, 255, dtype="uint8", endpoint=True), int)
assert_type(
    def_gen.integers(I_u1_low_like, 255, dtype="uint8", endpoint=True),
    npt.NDArray[np.uint8],
)
assert_type(def_gen.integers(I_u1_high_open, dtype="uint8"), npt.NDArray[np.uint8])
assert_type(
    def_gen.integers(I_u1_low, I_u1_high_open, dtype="uint8"), npt.NDArray[np.uint8]
)
assert_type(def_gen.integers(0, I_u1_high_open, dtype="uint8"), npt.NDArray[np.uint8])
assert_type(
    def_gen.integers(I_u1_high_closed, dtype="uint8", endpoint=True),
    npt.NDArray[np.uint8],
)
assert_type(
    def_gen.integers(I_u1_low, I_u1_high_closed, dtype="uint8", endpoint=True),
    npt.NDArray[np.uint8],
)
assert_type(
    def_gen.integers(0, I_u1_high_closed, dtype="uint8", endpoint=True),
    npt.NDArray[np.uint8],
)

assert_type(def_gen.integers(256, dtype=np.uint8), int)
assert_type(def_gen.integers(0, 256, dtype=np.uint8), int)
assert_type(def_gen.integers(255, dtype=np.uint8, endpoint=True), int)
assert_type(def_gen.integers(0, 255, dtype=np.uint8, endpoint=True), int)
assert_type(
    def_gen.integers(I_u1_low_like, 255, dtype=np.uint8, endpoint=True),
    npt.NDArray[np.uint8],
)
assert_type(def_gen.integers(I_u1_high_open, dtype=np.uint8), npt.NDArray[np.uint8])
assert_type(
    def_gen.integers(I_u1_low, I_u1_high_open, dtype=np.uint8), npt.NDArray[np.uint8]
)
assert_type(def_gen.integers(0, I_u1_high_open, dtype=np.uint8), npt.NDArray[np.uint8])
assert_type(
    def_gen.integers(I_u1_high_closed, dtype=np.uint8, endpoint=True),
    npt.NDArray[np.uint8],
)
assert_type(
    def_gen.integers(I_u1_low, I_u1_high_closed, dtype=np.uint8, endpoint=True),
    npt.NDArray[np.uint8],
)
assert_type(
    def_gen.integers(0, I_u1_high_closed, dtype=np.uint8, endpoint=True),
    npt.NDArray[np.uint8],
)

I_u2_low: np.ndarray[Any, np.dtype[np.uint16]] = np.array([0], dtype=np.uint16)
I_u2_low_like: list[int] = [0]
I_u2_high_open: np.ndarray[Any, np.dtype[np.uint16]] = np.array(
    [65535], dtype=np.uint16
)
I_u2_high_closed: np.ndarray[Any, np.dtype[np.uint16]] = np.array(
    [65535], dtype=np.uint16
)

assert_type(def_gen.integers(65536, dtype="u2"), int)
assert_type(def_gen.integers(0, 65536, dtype="u2"), int)
assert_type(def_gen.integers(65535, dtype="u2", endpoint=True), int)
assert_type(def_gen.integers(0, 65535, dtype="u2", endpoint=True), int)
assert_type(
    def_gen.integers(I_u2_low_like, 65535, dtype="u2", endpoint=True),
    npt.NDArray[np.uint16],
)
assert_type(def_gen.integers(I_u2_high_open, dtype="u2"), npt.NDArray[np.uint16])
assert_type(
    def_gen.integers(I_u2_low, I_u2_high_open, dtype="u2"), npt.NDArray[np.uint16]
)
assert_type(def_gen.integers(0, I_u2_high_open, dtype="u2"), npt.NDArray[np.uint16])
assert_type(
    def_gen.integers(I_u2_high_closed, dtype="u2", endpoint=True),
    npt.NDArray[np.uint16],
)
assert_type(
    def_gen.integers(I_u2_low, I_u2_high_closed, dtype="u2", endpoint=True),
    npt.NDArray[np.uint16],
)
assert_type(
    def_gen.integers(0, I_u2_high_closed, dtype="u2", endpoint=True),
    npt.NDArray[np.uint16],
)

assert_type(def_gen.integers(65536, dtype="uint16"), int)
assert_type(def_gen.integers(0, 65536, dtype="uint16"), int)
assert_type(def_gen.integers(65535, dtype="uint16", endpoint=True), int)
assert_type(def_gen.integers(0, 65535, dtype="uint16", endpoint=True), int)
assert_type(
    def_gen.integers(I_u2_low_like, 65535, dtype="uint16", endpoint=True),
    npt.NDArray[np.uint16],
)
assert_type(def_gen.integers(I_u2_high_open, dtype="uint16"), npt.NDArray[np.uint16])
assert_type(
    def_gen.integers(I_u2_low, I_u2_high_open, dtype="uint16"), npt.NDArray[np.uint16]
)
assert_type(def_gen.integers(0, I_u2_high_open, dtype="uint16"), npt.NDArray[np.uint16])
assert_type(
    def_gen.integers(I_u2_high_closed, dtype="uint16", endpoint=True),
    npt.NDArray[np.uint16],
)
assert_type(
    def_gen.integers(I_u2_low, I_u2_high_closed, dtype="uint16", endpoint=True),
    npt.NDArray[np.uint16],
)
assert_type(
    def_gen.integers(0, I_u2_high_closed, dtype="uint16", endpoint=True),
    npt.NDArray[np.uint16],
)

assert_type(def_gen.integers(65536, dtype=np.uint16), int)
assert_type(def_gen.integers(0, 65536, dtype=np.uint16), int)
assert_type(def_gen.integers(65535, dtype=np.uint16, endpoint=True), int)
assert_type(def_gen.integers(0, 65535, dtype=np.uint16, endpoint=True), int)
assert_type(
    def_gen.integers(I_u2_low_like, 65535, dtype=np.uint16, endpoint=True),
    npt.NDArray[np.uint16],
)
assert_type(def_gen.integers(I_u2_high_open, dtype=np.uint16), npt.NDArray[np.uint16])
assert_type(
    def_gen.integers(I_u2_low, I_u2_high_open, dtype=np.uint16), npt.NDArray[np.uint16]
)
assert_type(
    def_gen.integers(0, I_u2_high_open, dtype=np.uint16), npt.NDArray[np.uint16]
)
assert_type(
    def_gen.integers(I_u2_high_closed, dtype=np.uint16, endpoint=True),
    npt.NDArray[np.uint16],
)
assert_type(
    def_gen.integers(I_u2_low, I_u2_high_closed, dtype=np.uint16, endpoint=True),
    npt.NDArray[np.uint16],
)
assert_type(
    def_gen.integers(0, I_u2_high_closed, dtype=np.uint16, endpoint=True),
    npt.NDArray[np.uint16],
)

I_u4_low: np.ndarray[Any, np.dtype[np.uint32]] = np.array([0], dtype=np.uint32)
I_u4_low_like: list[int] = [0]
I_u4_high_open: np.ndarray[Any, np.dtype[np.uint32]] = np.array(
    [4294967295], dtype=np.uint32
)
I_u4_high_closed: np.ndarray[Any, np.dtype[np.uint32]] = np.array(
    [4294967295], dtype=np.uint32
)

assert_type(def_gen.integers(4294967296, dtype=np.int_), int)
assert_type(def_gen.integers(0, 4294967296, dtype=np.int_), int)
assert_type(def_gen.integers(4294967295, dtype=np.int_, endpoint=True), int)
assert_type(def_gen.integers(0, 4294967295, dtype=np.int_, endpoint=True), int)
assert_type(
    def_gen.integers(I_u4_low_like, 4294967295, dtype=np.int_, endpoint=True),
    npt.NDArray[np.int_],
)
assert_type(def_gen.integers(I_u4_high_open, dtype=np.int_), npt.NDArray[np.int_])
assert_type(
    def_gen.integers(I_u4_low, I_u4_high_open, dtype=np.int_), npt.NDArray[np.int_]
)
assert_type(def_gen.integers(0, I_u4_high_open, dtype=np.int_), npt.NDArray[np.int_])
assert_type(
    def_gen.integers(I_u4_high_closed, dtype=np.int_, endpoint=True),
    npt.NDArray[np.int_],
)
assert_type(
    def_gen.integers(I_u4_low, I_u4_high_closed, dtype=np.int_, endpoint=True),
    npt.NDArray[np.int_],
)
assert_type(
    def_gen.integers(0, I_u4_high_closed, dtype=np.int_, endpoint=True),
    npt.NDArray[np.int_],
)

assert_type(def_gen.integers(4294967296, dtype="u4"), int)
assert_type(def_gen.integers(0, 4294967296, dtype="u4"), int)
assert_type(def_gen.integers(4294967295, dtype="u4", endpoint=True), int)
assert_type(def_gen.integers(0, 4294967295, dtype="u4", endpoint=True), int)
assert_type(
    def_gen.integers(I_u4_low_like, 4294967295, dtype="u4", endpoint=True),
    npt.NDArray[np.uint32],
)
assert_type(def_gen.integers(I_u4_high_open, dtype="u4"), npt.NDArray[np.uint32])
assert_type(
    def_gen.integers(I_u4_low, I_u4_high_open, dtype="u4"), npt.NDArray[np.uint32]
)
assert_type(def_gen.integers(0, I_u4_high_open, dtype="u4"), npt.NDArray[np.uint32])
assert_type(
    def_gen.integers(I_u4_high_closed, dtype="u4", endpoint=True),
    npt.NDArray[np.uint32],
)
assert_type(
    def_gen.integers(I_u4_low, I_u4_high_closed, dtype="u4", endpoint=True),
    npt.NDArray[np.uint32],
)
assert_type(
    def_gen.integers(0, I_u4_high_closed, dtype="u4", endpoint=True),
    npt.NDArray[np.uint32],
)

assert_type(def_gen.integers(4294967296, dtype="uint32"), int)
assert_type(def_gen.integers(0, 4294967296, dtype="uint32"), int)
assert_type(def_gen.integers(4294967295, dtype="uint32", endpoint=True), int)
assert_type(def_gen.integers(0, 4294967295, dtype="uint32", endpoint=True), int)
assert_type(
    def_gen.integers(I_u4_low_like, 4294967295, dtype="uint32", endpoint=True),
    npt.NDArray[np.uint32],
)
assert_type(def_gen.integers(I_u4_high_open, dtype="uint32"), npt.NDArray[np.uint32])
assert_type(
    def_gen.integers(I_u4_low, I_u4_high_open, dtype="uint32"), npt.NDArray[np.uint32]
)
assert_type(def_gen.integers(0, I_u4_high_open, dtype="uint32"), npt.NDArray[np.uint32])
assert_type(
    def_gen.integers(I_u4_high_closed, dtype="uint32", endpoint=True),
    npt.NDArray[np.uint32],
)
assert_type(
    def_gen.integers(I_u4_low, I_u4_high_closed, dtype="uint32", endpoint=True),
    npt.NDArray[np.uint32],
)
assert_type(
    def_gen.integers(0, I_u4_high_closed, dtype="uint32", endpoint=True),
    npt.NDArray[np.uint32],
)

assert_type(def_gen.integers(4294967296, dtype=np.uint32), int)
assert_type(def_gen.integers(0, 4294967296, dtype=np.uint32), int)
assert_type(def_gen.integers(4294967295, dtype=np.uint32, endpoint=True), int)
assert_type(def_gen.integers(0, 4294967295, dtype=np.uint32, endpoint=True), int)
assert_type(
    def_gen.integers(I_u4_low_like, 4294967295, dtype=np.uint32, endpoint=True),
    npt.NDArray[np.uint32],
)
assert_type(def_gen.integers(I_u4_high_open, dtype=np.uint32), npt.NDArray[np.uint32])
assert_type(
    def_gen.integers(I_u4_low, I_u4_high_open, dtype=np.uint32), npt.NDArray[np.uint32]
)
assert_type(
    def_gen.integers(0, I_u4_high_open, dtype=np.uint32), npt.NDArray[np.uint32]
)
assert_type(
    def_gen.integers(I_u4_high_closed, dtype=np.uint32, endpoint=True),
    npt.NDArray[np.uint32],
)
assert_type(
    def_gen.integers(I_u4_low, I_u4_high_closed, dtype=np.uint32, endpoint=True),
    npt.NDArray[np.uint32],
)
assert_type(
    def_gen.integers(0, I_u4_high_closed, dtype=np.uint32, endpoint=True),
    npt.NDArray[np.uint32],
)

assert_type(def_gen.integers(4294967296, dtype=np.uint), int)
assert_type(def_gen.integers(0, 4294967296, dtype=np.uint), int)
assert_type(def_gen.integers(4294967295, dtype=np.uint, endpoint=True), int)
assert_type(def_gen.integers(0, 4294967295, dtype=np.uint, endpoint=True), int)
assert_type(
    def_gen.integers(I_u4_low_like, 4294967295, dtype=np.uint, endpoint=True),
    npt.NDArray[np.uint],
)
assert_type(def_gen.integers(I_u4_high_open, dtype=np.uint), npt.NDArray[np.uint])
assert_type(
    def_gen.integers(I_u4_low, I_u4_high_open, dtype=np.uint), npt.NDArray[np.uint]
)
assert_type(def_gen.integers(0, I_u4_high_open, dtype=np.uint), npt.NDArray[np.uint])
assert_type(
    def_gen.integers(I_u4_high_closed, dtype=np.uint, endpoint=True),
    npt.NDArray[np.uint],
)
assert_type(
    def_gen.integers(I_u4_low, I_u4_high_closed, dtype=np.uint, endpoint=True),
    npt.NDArray[np.uint],
)
assert_type(
    def_gen.integers(0, I_u4_high_closed, dtype=np.uint, endpoint=True),
    npt.NDArray[np.uint],
)

I_u8_low: np.ndarray[Any, np.dtype[np.uint64]] = np.array([0], dtype=np.uint64)
I_u8_low_like: list[int] = [0]
I_u8_high_open: np.ndarray[Any, np.dtype[np.uint64]] = np.array(
    [18446744073709551615], dtype=np.uint64
)
I_u8_high_closed: np.ndarray[Any, np.dtype[np.uint64]] = np.array(
    [18446744073709551615], dtype=np.uint64
)

assert_type(def_gen.integers(18446744073709551616, dtype="u8"), int)
assert_type(def_gen.integers(0, 18446744073709551616, dtype="u8"), int)
assert_type(def_gen.integers(18446744073709551615, dtype="u8", endpoint=True), int)
assert_type(def_gen.integers(0, 18446744073709551615, dtype="u8", endpoint=True), int)
assert_type(
    def_gen.integers(I_u8_low_like, 18446744073709551615, dtype="u8", endpoint=True),
    npt.NDArray[np.uint64],
)
assert_type(def_gen.integers(I_u8_high_open, dtype="u8"), npt.NDArray[np.uint64])
assert_type(
    def_gen.integers(I_u8_low, I_u8_high_open, dtype="u8"), npt.NDArray[np.uint64]
)
assert_type(def_gen.integers(0, I_u8_high_open, dtype="u8"), npt.NDArray[np.uint64])
assert_type(
    def_gen.integers(I_u8_high_closed, dtype="u8", endpoint=True),
    npt.NDArray[np.uint64],
)
assert_type(
    def_gen.integers(I_u8_low, I_u8_high_closed, dtype="u8", endpoint=True),
    npt.NDArray[np.uint64],
)
assert_type(
    def_gen.integers(0, I_u8_high_closed, dtype="u8", endpoint=True),
    npt.NDArray[np.uint64],
)

assert_type(def_gen.integers(18446744073709551616, dtype="uint64"), int)
assert_type(def_gen.integers(0, 18446744073709551616, dtype="uint64"), int)
assert_type(def_gen.integers(18446744073709551615, dtype="uint64", endpoint=True), int)
assert_type(
    def_gen.integers(0, 18446744073709551615, dtype="uint64", endpoint=True), int
)
assert_type(
    def_gen.integers(
        I_u8_low_like, 18446744073709551615, dtype="uint64", endpoint=True
    ),
    npt.NDArray[np.uint64],
)
assert_type(def_gen.integers(I_u8_high_open, dtype="uint64"), npt.NDArray[np.uint64])
assert_type(
    def_gen.integers(I_u8_low, I_u8_high_open, dtype="uint64"), npt.NDArray[np.uint64]
)
assert_type(def_gen.integers(0, I_u8_high_open, dtype="uint64"), npt.NDArray[np.uint64])
assert_type(
    def_gen.integers(I_u8_high_closed, dtype="uint64", endpoint=True),
    npt.NDArray[np.uint64],
)
assert_type(
    def_gen.integers(I_u8_low, I_u8_high_closed, dtype="uint64", endpoint=True),
    npt.NDArray[np.uint64],
)
assert_type(
    def_gen.integers(0, I_u8_high_closed, dtype="uint64", endpoint=True),
    npt.NDArray[np.uint64],
)

assert_type(def_gen.integers(18446744073709551616, dtype=np.uint64), int)
assert_type(def_gen.integers(0, 18446744073709551616, dtype=np.uint64), int)
assert_type(def_gen.integers(18446744073709551615, dtype=np.uint64, endpoint=True), int)
assert_type(
    def_gen.integers(0, 18446744073709551615, dtype=np.uint64, endpoint=True), int
)
assert_type(
    def_gen.integers(
        I_u8_low_like, 18446744073709551615, dtype=np.uint64, endpoint=True
    ),
    npt.NDArray[np.uint64],
)
assert_type(def_gen.integers(I_u8_high_open, dtype=np.uint64), npt.NDArray[np.uint64])
assert_type(
    def_gen.integers(I_u8_low, I_u8_high_open, dtype=np.uint64), npt.NDArray[np.uint64]
)
assert_type(
    def_gen.integers(0, I_u8_high_open, dtype=np.uint64), npt.NDArray[np.uint64]
)
assert_type(
    def_gen.integers(I_u8_high_closed, dtype=np.uint64, endpoint=True),
    npt.NDArray[np.uint64],
)
assert_type(
    def_gen.integers(I_u8_low, I_u8_high_closed, dtype=np.uint64, endpoint=True),
    npt.NDArray[np.uint64],
)
assert_type(
    def_gen.integers(0, I_u8_high_closed, dtype=np.uint64, endpoint=True),
    npt.NDArray[np.uint64],
)

I_i1_low: np.ndarray[Any, np.dtype[np.int8]] = np.array([-128], dtype=np.int8)
I_i1_low_like: list[int] = [-128]
I_i1_high_open: np.ndarray[Any, np.dtype[np.int8]] = np.array([127], dtype=np.int8)
I_i1_high_closed: np.ndarray[Any, np.dtype[np.int8]] = np.array([127], dtype=np.int8)

assert_type(def_gen.integers(128, dtype="i1"), int)
assert_type(def_gen.integers(-128, 128, dtype="i1"), int)
assert_type(def_gen.integers(127, dtype="i1", endpoint=True), int)
assert_type(def_gen.integers(-128, 127, dtype="i1", endpoint=True), int)
assert_type(
    def_gen.integers(I_i1_low_like, 127, dtype="i1", endpoint=True),
    npt.NDArray[np.int8],
)
assert_type(def_gen.integers(I_i1_high_open, dtype="i1"), npt.NDArray[np.int8])
assert_type(
    def_gen.integers(I_i1_low, I_i1_high_open, dtype="i1"), npt.NDArray[np.int8]
)
assert_type(def_gen.integers(-128, I_i1_high_open, dtype="i1"), npt.NDArray[np.int8])
assert_type(
    def_gen.integers(I_i1_high_closed, dtype="i1", endpoint=True), npt.NDArray[np.int8]
)
assert_type(
    def_gen.integers(I_i1_low, I_i1_high_closed, dtype="i1", endpoint=True),
    npt.NDArray[np.int8],
)
assert_type(
    def_gen.integers(-128, I_i1_high_closed, dtype="i1", endpoint=True),
    npt.NDArray[np.int8],
)

assert_type(def_gen.integers(128, dtype="int8"), int)
assert_type(def_gen.integers(-128, 128, dtype="int8"), int)
assert_type(def_gen.integers(127, dtype="int8", endpoint=True), int)
assert_type(def_gen.integers(-128, 127, dtype="int8", endpoint=True), int)
assert_type(
    def_gen.integers(I_i1_low_like, 127, dtype="int8", endpoint=True),
    npt.NDArray[np.int8],
)
assert_type(def_gen.integers(I_i1_high_open, dtype="int8"), npt.NDArray[np.int8])
assert_type(
    def_gen.integers(I_i1_low, I_i1_high_open, dtype="int8"), npt.NDArray[np.int8]
)
assert_type(def_gen.integers(-128, I_i1_high_open, dtype="int8"), npt.NDArray[np.int8])
assert_type(
    def_gen.integers(I_i1_high_closed, dtype="int8", endpoint=True),
    npt.NDArray[np.int8],
)
assert_type(
    def_gen.integers(I_i1_low, I_i1_high_closed, dtype="int8", endpoint=True),
    npt.NDArray[np.int8],
)
assert_type(
    def_gen.integers(-128, I_i1_high_closed, dtype="int8", endpoint=True),
    npt.NDArray[np.int8],
)

assert_type(def_gen.integers(128, dtype=np.int8), int)
assert_type(def_gen.integers(-128, 128, dtype=np.int8), int)
assert_type(def_gen.integers(127, dtype=np.int8, endpoint=True), int)
assert_type(def_gen.integers(-128, 127, dtype=np.int8, endpoint=True), int)
assert_type(
    def_gen.integers(I_i1_low_like, 127, dtype=np.int8, endpoint=True),
    npt.NDArray[np.int8],
)
assert_type(def_gen.integers(I_i1_high_open, dtype=np.int8), npt.NDArray[np.int8])
assert_type(
    def_gen.integers(I_i1_low, I_i1_high_open, dtype=np.int8), npt.NDArray[np.int8]
)
assert_type(def_gen.integers(-128, I_i1_high_open, dtype=np.int8), npt.NDArray[np.int8])
assert_type(
    def_gen.integers(I_i1_high_closed, dtype=np.int8, endpoint=True),
    npt.NDArray[np.int8],
)
assert_type(
    def_gen.integers(I_i1_low, I_i1_high_closed, dtype=np.int8, endpoint=True),
    npt.NDArray[np.int8],
)
assert_type(
    def_gen.integers(-128, I_i1_high_closed, dtype=np.int8, endpoint=True),
    npt.NDArray[np.int8],
)

I_i2_low: npt.NDArray[np.int16] = np.array([-32768], dtype=np.int16)
I_i2_low_like: list[int] = [-32768]
I_i2_high_open: npt.NDArray[np.int16] = np.array([32767], dtype=np.int16)
I_i2_high_closed: npt.NDArray[np.int16] = np.array([32767], dtype=np.int16)

assert_type(def_gen.integers(32768, dtype="i2"), int)
assert_type(def_gen.integers(-32768, 32768, dtype="i2"), int)
assert_type(def_gen.integers(32767, dtype="i2", endpoint=True), int)
assert_type(def_gen.integers(-32768, 32767, dtype="i2", endpoint=True), int)
assert_type(
    def_gen.integers(I_i2_low_like, 32767, dtype="i2", endpoint=True),
    npt.NDArray[np.int16],
)
assert_type(def_gen.integers(I_i2_high_open, dtype="i2"), npt.NDArray[np.int16])
assert_type(
    def_gen.integers(I_i2_low, I_i2_high_open, dtype="i2"), npt.NDArray[np.int16]
)
assert_type(def_gen.integers(-32768, I_i2_high_open, dtype="i2"), npt.NDArray[np.int16])
assert_type(
    def_gen.integers(I_i2_high_closed, dtype="i2", endpoint=True), npt.NDArray[np.int16]
)
assert_type(
    def_gen.integers(I_i2_low, I_i2_high_closed, dtype="i2", endpoint=True),
    npt.NDArray[np.int16],
)
assert_type(
    def_gen.integers(-32768, I_i2_high_closed, dtype="i2", endpoint=True),
    npt.NDArray[np.int16],
)

assert_type(def_gen.integers(32768, dtype="int16"), int)
assert_type(def_gen.integers(-32768, 32768, dtype="int16"), int)
assert_type(def_gen.integers(32767, dtype="int16", endpoint=True), int)
assert_type(def_gen.integers(-32768, 32767, dtype="int16", endpoint=True), int)
assert_type(
    def_gen.integers(I_i2_low_like, 32767, dtype="int16", endpoint=True),
    npt.NDArray[np.int16],
)
assert_type(def_gen.integers(I_i2_high_open, dtype="int16"), npt.NDArray[np.int16])
assert_type(
    def_gen.integers(I_i2_low, I_i2_high_open, dtype="int16"), npt.NDArray[np.int16]
)
assert_type(
    def_gen.integers(-32768, I_i2_high_open, dtype="int16"), npt.NDArray[np.int16]
)
assert_type(
    def_gen.integers(I_i2_high_closed, dtype="int16", endpoint=True),
    npt.NDArray[np.int16],
)
assert_type(
    def_gen.integers(I_i2_low, I_i2_high_closed, dtype="int16", endpoint=True),
    npt.NDArray[np.int16],
)
assert_type(
    def_gen.integers(-32768, I_i2_high_closed, dtype="int16", endpoint=True),
    npt.NDArray[np.int16],
)

assert_type(def_gen.integers(32768, dtype=np.int16), int)
assert_type(def_gen.integers(-32768, 32768, dtype=np.int16), int)
assert_type(def_gen.integers(32767, dtype=np.int16, endpoint=True), int)
assert_type(def_gen.integers(-32768, 32767, dtype=np.int16, endpoint=True), int)
assert_type(
    def_gen.integers(I_i2_low_like, 32767, dtype=np.int16, endpoint=True),
    npt.NDArray[np.int16],
)
assert_type(def_gen.integers(I_i2_high_open, dtype=np.int16), npt.NDArray[np.int16])
assert_type(
    def_gen.integers(I_i2_low, I_i2_high_open, dtype=np.int16), npt.NDArray[np.int16]
)
assert_type(
    def_gen.integers(-32768, I_i2_high_open, dtype=np.int16), npt.NDArray[np.int16]
)
assert_type(
    def_gen.integers(I_i2_high_closed, dtype=np.int16, endpoint=True),
    npt.NDArray[np.int16],
)
assert_type(
    def_gen.integers(I_i2_low, I_i2_high_closed, dtype=np.int16, endpoint=True),
    npt.NDArray[np.int16],
)
assert_type(
    def_gen.integers(-32768, I_i2_high_closed, dtype=np.int16, endpoint=True),
    npt.NDArray[np.int16],
)

I_i4_low: np.ndarray[Any, np.dtype[np.int32]] = np.array([-2147483648], dtype=np.int32)
I_i4_low_like: list[int] = [-2147483648]
I_i4_high_open: np.ndarray[Any, np.dtype[np.int32]] = np.array(
    [2147483647], dtype=np.int32
)
I_i4_high_closed: np.ndarray[Any, np.dtype[np.int32]] = np.array(
    [2147483647], dtype=np.int32
)

assert_type(def_gen.integers(2147483648, dtype="i4"), int)
assert_type(def_gen.integers(-2147483648, 2147483648, dtype="i4"), int)
assert_type(def_gen.integers(2147483647, dtype="i4", endpoint=True), int)
assert_type(def_gen.integers(-2147483648, 2147483647, dtype="i4", endpoint=True), int)
assert_type(
    def_gen.integers(I_i4_low_like, 2147483647, dtype="i4", endpoint=True),
    npt.NDArray[np.int32],
)
assert_type(def_gen.integers(I_i4_high_open, dtype="i4"), npt.NDArray[np.int32])
assert_type(
    def_gen.integers(I_i4_low, I_i4_high_open, dtype="i4"), npt.NDArray[np.int32]
)
assert_type(
    def_gen.integers(-2147483648, I_i4_high_open, dtype="i4"), npt.NDArray[np.int32]
)
assert_type(
    def_gen.integers(I_i4_high_closed, dtype="i4", endpoint=True), npt.NDArray[np.int32]
)
assert_type(
    def_gen.integers(I_i4_low, I_i4_high_closed, dtype="i4", endpoint=True),
    npt.NDArray[np.int32],
)
assert_type(
    def_gen.integers(-2147483648, I_i4_high_closed, dtype="i4", endpoint=True),
    npt.NDArray[np.int32],
)

assert_type(def_gen.integers(2147483648, dtype="int32"), int)
assert_type(def_gen.integers(-2147483648, 2147483648, dtype="int32"), int)
assert_type(def_gen.integers(2147483647, dtype="int32", endpoint=True), int)
assert_type(
    def_gen.integers(-2147483648, 2147483647, dtype="int32", endpoint=True), int
)
assert_type(
    def_gen.integers(I_i4_low_like, 2147483647, dtype="int32", endpoint=True),
    npt.NDArray[np.int32],
)
assert_type(def_gen.integers(I_i4_high_open, dtype="int32"), npt.NDArray[np.int32])
assert_type(
    def_gen.integers(I_i4_low, I_i4_high_open, dtype="int32"), npt.NDArray[np.int32]
)
assert_type(
    def_gen.integers(-2147483648, I_i4_high_open, dtype="int32"), npt.NDArray[np.int32]
)
assert_type(
    def_gen.integers(I_i4_high_closed, dtype="int32", endpoint=True),
    npt.NDArray[np.int32],
)
assert_type(
    def_gen.integers(I_i4_low, I_i4_high_closed, dtype="int32", endpoint=True),
    npt.NDArray[np.int32],
)
assert_type(
    def_gen.integers(-2147483648, I_i4_high_closed, dtype="int32", endpoint=True),
    npt.NDArray[np.int32],
)

assert_type(def_gen.integers(2147483648, dtype=np.int32), int)
assert_type(def_gen.integers(-2147483648, 2147483648, dtype=np.int32), int)
assert_type(def_gen.integers(2147483647, dtype=np.int32, endpoint=True), int)
assert_type(
    def_gen.integers(-2147483648, 2147483647, dtype=np.int32, endpoint=True), int
)
assert_type(
    def_gen.integers(I_i4_low_like, 2147483647, dtype=np.int32, endpoint=True),
    npt.NDArray[np.int32],
)
assert_type(def_gen.integers(I_i4_high_open, dtype=np.int32), npt.NDArray[np.int32])
assert_type(
    def_gen.integers(I_i4_low, I_i4_high_open, dtype=np.int32), npt.NDArray[np.int32]
)
assert_type(
    def_gen.integers(-2147483648, I_i4_high_open, dtype=np.int32), npt.NDArray[np.int32]
)
assert_type(
    def_gen.integers(I_i4_high_closed, dtype=np.int32, endpoint=True),
    npt.NDArray[np.int32],
)
assert_type(
    def_gen.integers(I_i4_low, I_i4_high_closed, dtype=np.int32, endpoint=True),
    npt.NDArray[np.int32],
)
assert_type(
    def_gen.integers(-2147483648, I_i4_high_closed, dtype=np.int32, endpoint=True),
    npt.NDArray[np.int32],
)

I_i8_low: np.ndarray[Any, np.dtype[np.int64]] = np.array(
    [-9223372036854775808], dtype=np.int64
)
I_i8_low_like: list[int] = [-9223372036854775808]
I_i8_high_open: np.ndarray[Any, np.dtype[np.int64]] = np.array(
    [9223372036854775807], dtype=np.int64
)
I_i8_high_closed: np.ndarray[Any, np.dtype[np.int64]] = np.array(
    [9223372036854775807], dtype=np.int64
)

assert_type(def_gen.integers(9223372036854775808, dtype="i8"), int)
assert_type(
    def_gen.integers(-9223372036854775808, 9223372036854775808, dtype="i8"), int
)
assert_type(def_gen.integers(9223372036854775807, dtype="i8", endpoint=True), int)
assert_type(
    def_gen.integers(
        -9223372036854775808, 9223372036854775807, dtype="i8", endpoint=True
    ),
    int,
)
assert_type(
    def_gen.integers(I_i8_low_like, 9223372036854775807, dtype="i8", endpoint=True),
    npt.NDArray[np.int64],
)
assert_type(def_gen.integers(I_i8_high_open, dtype="i8"), npt.NDArray[np.int64])
assert_type(
    def_gen.integers(I_i8_low, I_i8_high_open, dtype="i8"), npt.NDArray[np.int64]
)
assert_type(
    def_gen.integers(-9223372036854775808, I_i8_high_open, dtype="i8"),
    npt.NDArray[np.int64],
)
assert_type(
    def_gen.integers(I_i8_high_closed, dtype="i8", endpoint=True), npt.NDArray[np.int64]
)
assert_type(
    def_gen.integers(I_i8_low, I_i8_high_closed, dtype="i8", endpoint=True),
    npt.NDArray[np.int64],
)
assert_type(
    def_gen.integers(-9223372036854775808, I_i8_high_closed, dtype="i8", endpoint=True),
    npt.NDArray[np.int64],
)

assert_type(def_gen.integers(9223372036854775808, dtype="int64"), int)
assert_type(
    def_gen.integers(-9223372036854775808, 9223372036854775808, dtype="int64"), int
)
assert_type(def_gen.integers(9223372036854775807, dtype="int64", endpoint=True), int)
assert_type(
    def_gen.integers(
        -9223372036854775808, 9223372036854775807, dtype="int64", endpoint=True
    ),
    int,
)
assert_type(
    def_gen.integers(I_i8_low_like, 9223372036854775807, dtype="int64", endpoint=True),
    npt.NDArray[np.int64],
)
assert_type(def_gen.integers(I_i8_high_open, dtype="int64"), npt.NDArray[np.int64])
assert_type(
    def_gen.integers(I_i8_low, I_i8_high_open, dtype="int64"), npt.NDArray[np.int64]
)
assert_type(
    def_gen.integers(-9223372036854775808, I_i8_high_open, dtype="int64"),
    npt.NDArray[np.int64],
)
assert_type(
    def_gen.integers(I_i8_high_closed, dtype="int64", endpoint=True),
    npt.NDArray[np.int64],
)
assert_type(
    def_gen.integers(I_i8_low, I_i8_high_closed, dtype="int64", endpoint=True),
    npt.NDArray[np.int64],
)
assert_type(
    def_gen.integers(
        -9223372036854775808, I_i8_high_closed, dtype="int64", endpoint=True
    ),
    npt.NDArray[np.int64],
)

assert_type(def_gen.integers(9223372036854775808, dtype=np.int64), int)
assert_type(
    def_gen.integers(-9223372036854775808, 9223372036854775808, dtype=np.int64), int
)
assert_type(def_gen.integers(9223372036854775807, dtype=np.int64, endpoint=True), int)
assert_type(
    def_gen.integers(
        -9223372036854775808, 9223372036854775807, dtype=np.int64, endpoint=True
    ),
    int,
)
assert_type(
    def_gen.integers(I_i8_low_like, 9223372036854775807, dtype=np.int64, endpoint=True),
    npt.NDArray[np.int64],
)
assert_type(def_gen.integers(I_i8_high_open, dtype=np.int64), npt.NDArray[np.int64])
assert_type(
    def_gen.integers(I_i8_low, I_i8_high_open, dtype=np.int64), npt.NDArray[np.int64]
)
assert_type(
    def_gen.integers(-9223372036854775808, I_i8_high_open, dtype=np.int64),
    npt.NDArray[np.int64],
)
assert_type(
    def_gen.integers(I_i8_high_closed, dtype=np.int64, endpoint=True),
    npt.NDArray[np.int64],
)
assert_type(
    def_gen.integers(I_i8_low, I_i8_high_closed, dtype=np.int64, endpoint=True),
    npt.NDArray[np.int64],
)
assert_type(
    def_gen.integers(
        -9223372036854775808, I_i8_high_closed, dtype=np.int64, endpoint=True
    ),
    npt.NDArray[np.int64],
)

assert_type(def_gen.bit_generator, np.random.BitGenerator)

assert_type(def_gen.bytes(2), bytes)

assert_type(def_gen.choice(5), int)
assert_type(def_gen.choice(5, 3), npt.NDArray[np.int64])
assert_type(def_gen.choice(5, 3, replace=True), npt.NDArray[np.int64])
assert_type(def_gen.choice(5, 3, p=[1 / 5] * 5), npt.NDArray[np.int64])
assert_type(def_gen.choice(5, 3, p=[1 / 5] * 5, replace=False), npt.NDArray[np.int64])

assert_type(def_gen.choice(["pooh", "rabbit", "piglet", "Christopher"]), Any)
assert_type(
    def_gen.choice(["pooh", "rabbit", "piglet", "Christopher"], 3), np.ndarray[Any, Any]
)
assert_type(
    def_gen.choice(["pooh", "rabbit", "piglet", "Christopher"], 3, p=[1 / 4] * 4),
    np.ndarray[Any, Any],
)
assert_type(
    def_gen.choice(["pooh", "rabbit", "piglet", "Christopher"], 3, replace=True),
    np.ndarray[Any, Any],
)
assert_type(
    def_gen.choice(
        ["pooh", "rabbit", "piglet", "Christopher"],
        3,
        replace=False,
        p=np.array([1 / 8, 1 / 8, 1 / 2, 1 / 4]),
    ),
    np.ndarray[Any, Any],
)

assert_type(def_gen.dirichlet([0.5, 0.5]), npt.NDArray[np.float64])
assert_type(def_gen.dirichlet(np.array([0.5, 0.5])), npt.NDArray[np.float64])
assert_type(def_gen.dirichlet(np.array([0.5, 0.5]), size=3), npt.NDArray[np.float64])

assert_type(def_gen.multinomial(20, [1 / 6.0] * 6), npt.NDArray[np.int64])
assert_type(def_gen.multinomial(20, np.array([0.5, 0.5])), npt.NDArray[np.int64])
assert_type(def_gen.multinomial(20, [1 / 6.0] * 6, size=2), npt.NDArray[np.int64])
assert_type(
    def_gen.multinomial([[10], [20]], [1 / 6.0] * 6, size=(2, 2)), npt.NDArray[np.int64]
)
assert_type(
    def_gen.multinomial(np.array([[10], [20]]), np.array([0.5, 0.5]), size=(2, 2)),
    npt.NDArray[np.int64],
)

assert_type(def_gen.multivariate_hypergeometric([3, 5, 7], 2), npt.NDArray[np.int64])
assert_type(
    def_gen.multivariate_hypergeometric(np.array([3, 5, 7]), 2), npt.NDArray[np.int64]
)
assert_type(
    def_gen.multivariate_hypergeometric(np.array([3, 5, 7]), 2, size=4),
    npt.NDArray[np.int64],
)
assert_type(
    def_gen.multivariate_hypergeometric(np.array([3, 5, 7]), 2, size=(4, 7)),
    npt.NDArray[np.int64],
)
assert_type(
    def_gen.multivariate_hypergeometric([3, 5, 7], 2, method="count"),
    npt.NDArray[np.int64],
)
assert_type(
    def_gen.multivariate_hypergeometric(np.array([3, 5, 7]), 2, method="marginals"),
    npt.NDArray[np.int64],
)

assert_type(def_gen.multivariate_normal([0.0], [[1.0]]), npt.NDArray[np.float64])
assert_type(
    def_gen.multivariate_normal([0.0], np.array([[1.0]])), npt.NDArray[np.float64]
)
assert_type(
    def_gen.multivariate_normal(np.array([0.0]), [[1.0]]), npt.NDArray[np.float64]
)
assert_type(
    def_gen.multivariate_normal([0.0], np.array([[1.0]])), npt.NDArray[np.float64]
)

assert_type(def_gen.permutation(10), npt.NDArray[np.int64])
assert_type(def_gen.permutation([1, 2, 3, 4]), np.ndarray[Any, Any])
assert_type(def_gen.permutation(np.array([1, 2, 3, 4])), np.ndarray[Any, Any])
assert_type(def_gen.permutation(D_2D, axis=1), np.ndarray[Any, Any])
assert_type(def_gen.permuted(D_2D), np.ndarray[Any, Any])
assert_type(def_gen.permuted(D_2D_like), np.ndarray[Any, Any])
assert_type(def_gen.permuted(D_2D, axis=1), np.ndarray[Any, Any])
assert_type(def_gen.permuted(D_2D, out=D_2D), np.ndarray[Any, Any])
assert_type(def_gen.permuted(D_2D_like, out=D_2D), np.ndarray[Any, Any])
assert_type(def_gen.permuted(D_2D_like, out=D_2D), np.ndarray[Any, Any])
assert_type(def_gen.permuted(D_2D, axis=1, out=D_2D), np.ndarray[Any, Any])

assert_type(def_gen.shuffle(np.arange(10)), None)
assert_type(def_gen.shuffle([1, 2, 3, 4, 5]), None)
assert_type(def_gen.shuffle(D_2D, axis=1), None)

assert_type(np.random.Generator(pcg64), np.random.Generator)
assert_type(def_gen.__str__(), str)
assert_type(def_gen.__repr__(), str)
def_gen_state = def_gen.__getstate__()
assert_type(def_gen_state, dict[str, Any])
assert_type(def_gen.__setstate__(def_gen_state), None)

# RandomState
random_st: np.random.RandomState = np.random.RandomState()

assert_type(random_st.standard_normal(), float)
assert_type(random_st.standard_normal(size=None), float)
assert_type(random_st.standard_normal(size=1), npt.NDArray[np.float64])

assert_type(random_st.random(), float)
assert_type(random_st.random(size=None), float)
assert_type(random_st.random(size=1), npt.NDArray[np.float64])

assert_type(random_st.standard_cauchy(), float)
assert_type(random_st.standard_cauchy(size=None), float)
assert_type(random_st.standard_cauchy(size=1), npt.NDArray[np.float64])

assert_type(random_st.standard_exponential(), float)
assert_type(random_st.standard_exponential(size=None), float)
assert_type(random_st.standard_exponential(size=1), npt.NDArray[np.float64])

assert_type(random_st.zipf(1.5), int)
assert_type(random_st.zipf(1.5, size=None), int)
assert_type(random_st.zipf(1.5, size=1), npt.NDArray[np.int_])
assert_type(random_st.zipf(D_arr_1p5), npt.NDArray[np.int_])
assert_type(random_st.zipf(D_arr_1p5, size=1), npt.NDArray[np.int_])
assert_type(random_st.zipf(D_arr_like_1p5), npt.NDArray[np.int_])
assert_type(random_st.zipf(D_arr_like_1p5, size=1), npt.NDArray[np.int_])

assert_type(random_st.weibull(0.5), float)
assert_type(random_st.weibull(0.5, size=None), float)
assert_type(random_st.weibull(0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.weibull(D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.weibull(D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(random_st.weibull(D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.weibull(D_arr_like_0p5, size=1), npt.NDArray[np.float64])

assert_type(random_st.standard_t(0.5), float)
assert_type(random_st.standard_t(0.5, size=None), float)
assert_type(random_st.standard_t(0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.standard_t(D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.standard_t(D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(random_st.standard_t(D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.standard_t(D_arr_like_0p5, size=1), npt.NDArray[np.float64])

assert_type(random_st.poisson(0.5), int)
assert_type(random_st.poisson(0.5, size=None), int)
assert_type(random_st.poisson(0.5, size=1), npt.NDArray[np.int_])
assert_type(random_st.poisson(D_arr_0p5), npt.NDArray[np.int_])
assert_type(random_st.poisson(D_arr_0p5, size=1), npt.NDArray[np.int_])
assert_type(random_st.poisson(D_arr_like_0p5), npt.NDArray[np.int_])
assert_type(random_st.poisson(D_arr_like_0p5, size=1), npt.NDArray[np.int_])

assert_type(random_st.power(0.5), float)
assert_type(random_st.power(0.5, size=None), float)
assert_type(random_st.power(0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.power(D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.power(D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(random_st.power(D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.power(D_arr_like_0p5, size=1), npt.NDArray[np.float64])

assert_type(random_st.pareto(0.5), float)
assert_type(random_st.pareto(0.5, size=None), float)
assert_type(random_st.pareto(0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.pareto(D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.pareto(D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(random_st.pareto(D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.pareto(D_arr_like_0p5, size=1), npt.NDArray[np.float64])

assert_type(random_st.chisquare(0.5), float)
assert_type(random_st.chisquare(0.5, size=None), float)
assert_type(random_st.chisquare(0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.chisquare(D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.chisquare(D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(random_st.chisquare(D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.chisquare(D_arr_like_0p5, size=1), npt.NDArray[np.float64])

assert_type(random_st.exponential(0.5), float)
assert_type(random_st.exponential(0.5, size=None), float)
assert_type(random_st.exponential(0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.exponential(D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.exponential(D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(random_st.exponential(D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.exponential(D_arr_like_0p5, size=1), npt.NDArray[np.float64])

assert_type(random_st.geometric(0.5), int)
assert_type(random_st.geometric(0.5, size=None), int)
assert_type(random_st.geometric(0.5, size=1), npt.NDArray[np.int_])
assert_type(random_st.geometric(D_arr_0p5), npt.NDArray[np.int_])
assert_type(random_st.geometric(D_arr_0p5, size=1), npt.NDArray[np.int_])
assert_type(random_st.geometric(D_arr_like_0p5), npt.NDArray[np.int_])
assert_type(random_st.geometric(D_arr_like_0p5, size=1), npt.NDArray[np.int_])

assert_type(random_st.logseries(0.5), int)
assert_type(random_st.logseries(0.5, size=None), int)
assert_type(random_st.logseries(0.5, size=1), npt.NDArray[np.int_])
assert_type(random_st.logseries(D_arr_0p5), npt.NDArray[np.int_])
assert_type(random_st.logseries(D_arr_0p5, size=1), npt.NDArray[np.int_])
assert_type(random_st.logseries(D_arr_like_0p5), npt.NDArray[np.int_])
assert_type(random_st.logseries(D_arr_like_0p5, size=1), npt.NDArray[np.int_])

assert_type(random_st.rayleigh(0.5), float)
assert_type(random_st.rayleigh(0.5, size=None), float)
assert_type(random_st.rayleigh(0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.rayleigh(D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.rayleigh(D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(random_st.rayleigh(D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.rayleigh(D_arr_like_0p5, size=1), npt.NDArray[np.float64])

assert_type(random_st.standard_gamma(0.5), float)
assert_type(random_st.standard_gamma(0.5, size=None), float)
assert_type(random_st.standard_gamma(0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.standard_gamma(D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.standard_gamma(D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(random_st.standard_gamma(D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.standard_gamma(D_arr_like_0p5, size=1), npt.NDArray[np.float64])
assert_type(random_st.standard_gamma(D_arr_like_0p5, size=1), npt.NDArray[np.float64])

assert_type(random_st.vonmises(0.5, 0.5), float)
assert_type(random_st.vonmises(0.5, 0.5, size=None), float)
assert_type(random_st.vonmises(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.vonmises(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.vonmises(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.vonmises(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.vonmises(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(random_st.vonmises(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.vonmises(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.vonmises(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.vonmises(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.vonmises(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    random_st.vonmises(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64]
)

assert_type(random_st.wald(0.5, 0.5), float)
assert_type(random_st.wald(0.5, 0.5, size=None), float)
assert_type(random_st.wald(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.wald(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.wald(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.wald(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.wald(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(random_st.wald(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.wald(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.wald(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.wald(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.wald(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    random_st.wald(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64]
)

assert_type(random_st.uniform(0.5, 0.5), float)
assert_type(random_st.uniform(0.5, 0.5, size=None), float)
assert_type(random_st.uniform(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.uniform(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.uniform(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.uniform(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.uniform(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(random_st.uniform(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.uniform(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.uniform(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.uniform(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.uniform(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    random_st.uniform(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64]
)

assert_type(random_st.beta(0.5, 0.5), float)
assert_type(random_st.beta(0.5, 0.5, size=None), float)
assert_type(random_st.beta(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.beta(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.beta(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.beta(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.beta(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(random_st.beta(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.beta(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.beta(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.beta(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.beta(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    random_st.beta(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64]
)

assert_type(random_st.f(0.5, 0.5), float)
assert_type(random_st.f(0.5, 0.5, size=None), float)
assert_type(random_st.f(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.f(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.f(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.f(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.f(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(random_st.f(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.f(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.f(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.f(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.f(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    random_st.f(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64]
)

assert_type(random_st.gamma(0.5, 0.5), float)
assert_type(random_st.gamma(0.5, 0.5, size=None), float)
assert_type(random_st.gamma(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.gamma(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.gamma(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.gamma(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.gamma(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(random_st.gamma(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.gamma(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.gamma(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.gamma(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.gamma(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    random_st.gamma(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64]
)

assert_type(random_st.gumbel(0.5, 0.5), float)
assert_type(random_st.gumbel(0.5, 0.5, size=None), float)
assert_type(random_st.gumbel(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.gumbel(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.gumbel(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.gumbel(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.gumbel(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(random_st.gumbel(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.gumbel(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.gumbel(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.gumbel(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.gumbel(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    random_st.gumbel(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64]
)

assert_type(random_st.laplace(0.5, 0.5), float)
assert_type(random_st.laplace(0.5, 0.5, size=None), float)
assert_type(random_st.laplace(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.laplace(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.laplace(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.laplace(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.laplace(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(random_st.laplace(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.laplace(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.laplace(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.laplace(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.laplace(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    random_st.laplace(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64]
)

assert_type(random_st.logistic(0.5, 0.5), float)
assert_type(random_st.logistic(0.5, 0.5, size=None), float)
assert_type(random_st.logistic(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.logistic(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.logistic(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.logistic(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.logistic(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(random_st.logistic(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.logistic(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.logistic(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.logistic(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.logistic(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    random_st.logistic(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64]
)

assert_type(random_st.lognormal(0.5, 0.5), float)
assert_type(random_st.lognormal(0.5, 0.5, size=None), float)
assert_type(random_st.lognormal(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.lognormal(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.lognormal(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.lognormal(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.lognormal(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(random_st.lognormal(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.lognormal(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.lognormal(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(
    random_st.lognormal(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64]
)
assert_type(random_st.lognormal(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    random_st.lognormal(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64]
)

assert_type(random_st.noncentral_chisquare(0.5, 0.5), float)
assert_type(random_st.noncentral_chisquare(0.5, 0.5, size=None), float)
assert_type(random_st.noncentral_chisquare(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.noncentral_chisquare(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.noncentral_chisquare(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(
    random_st.noncentral_chisquare(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64]
)
assert_type(
    random_st.noncentral_chisquare(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64]
)
assert_type(
    random_st.noncentral_chisquare(D_arr_like_0p5, 0.5), npt.NDArray[np.float64]
)
assert_type(
    random_st.noncentral_chisquare(0.5, D_arr_like_0p5), npt.NDArray[np.float64]
)
assert_type(
    random_st.noncentral_chisquare(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64]
)
assert_type(
    random_st.noncentral_chisquare(D_arr_like_0p5, D_arr_like_0p5),
    npt.NDArray[np.float64],
)
assert_type(
    random_st.noncentral_chisquare(D_arr_0p5, D_arr_0p5, size=1),
    npt.NDArray[np.float64],
)
assert_type(
    random_st.noncentral_chisquare(D_arr_like_0p5, D_arr_like_0p5, size=1),
    npt.NDArray[np.float64],
)

assert_type(random_st.normal(0.5, 0.5), float)
assert_type(random_st.normal(0.5, 0.5, size=None), float)
assert_type(random_st.normal(0.5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.normal(D_arr_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.normal(0.5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.normal(D_arr_0p5, 0.5, size=1), npt.NDArray[np.float64])
assert_type(random_st.normal(0.5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(random_st.normal(D_arr_like_0p5, 0.5), npt.NDArray[np.float64])
assert_type(random_st.normal(0.5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.normal(D_arr_0p5, D_arr_0p5), npt.NDArray[np.float64])
assert_type(random_st.normal(D_arr_like_0p5, D_arr_like_0p5), npt.NDArray[np.float64])
assert_type(random_st.normal(D_arr_0p5, D_arr_0p5, size=1), npt.NDArray[np.float64])
assert_type(
    random_st.normal(D_arr_like_0p5, D_arr_like_0p5, size=1), npt.NDArray[np.float64]
)

assert_type(random_st.triangular(0.1, 0.5, 0.9), float)
assert_type(random_st.triangular(0.1, 0.5, 0.9, size=None), float)
assert_type(random_st.triangular(0.1, 0.5, 0.9, size=1), npt.NDArray[np.float64])
assert_type(random_st.triangular(D_arr_0p1, 0.5, 0.9), npt.NDArray[np.float64])
assert_type(random_st.triangular(0.1, D_arr_0p5, 0.9), npt.NDArray[np.float64])
assert_type(
    random_st.triangular(D_arr_0p1, 0.5, D_arr_like_0p9, size=1),
    npt.NDArray[np.float64],
)
assert_type(random_st.triangular(0.1, D_arr_0p5, 0.9, size=1), npt.NDArray[np.float64])
assert_type(
    random_st.triangular(D_arr_like_0p1, 0.5, D_arr_0p9), npt.NDArray[np.float64]
)
assert_type(random_st.triangular(0.5, D_arr_like_0p5, 0.9), npt.NDArray[np.float64])
assert_type(random_st.triangular(D_arr_0p1, D_arr_0p5, 0.9), npt.NDArray[np.float64])
assert_type(
    random_st.triangular(D_arr_like_0p1, D_arr_like_0p5, 0.9), npt.NDArray[np.float64]
)
assert_type(
    random_st.triangular(D_arr_0p1, D_arr_0p5, D_arr_0p9, size=1),
    npt.NDArray[np.float64],
)
assert_type(
    random_st.triangular(D_arr_like_0p1, D_arr_like_0p5, D_arr_like_0p9, size=1),
    npt.NDArray[np.float64],
)

assert_type(random_st.noncentral_f(0.1, 0.5, 0.9), float)
assert_type(random_st.noncentral_f(0.1, 0.5, 0.9, size=None), float)
assert_type(random_st.noncentral_f(0.1, 0.5, 0.9, size=1), npt.NDArray[np.float64])
assert_type(random_st.noncentral_f(D_arr_0p1, 0.5, 0.9), npt.NDArray[np.float64])
assert_type(random_st.noncentral_f(0.1, D_arr_0p5, 0.9), npt.NDArray[np.float64])
assert_type(
    random_st.noncentral_f(D_arr_0p1, 0.5, D_arr_like_0p9, size=1),
    npt.NDArray[np.float64],
)
assert_type(
    random_st.noncentral_f(0.1, D_arr_0p5, 0.9, size=1), npt.NDArray[np.float64]
)
assert_type(
    random_st.noncentral_f(D_arr_like_0p1, 0.5, D_arr_0p9), npt.NDArray[np.float64]
)
assert_type(random_st.noncentral_f(0.5, D_arr_like_0p5, 0.9), npt.NDArray[np.float64])
assert_type(random_st.noncentral_f(D_arr_0p1, D_arr_0p5, 0.9), npt.NDArray[np.float64])
assert_type(
    random_st.noncentral_f(D_arr_like_0p1, D_arr_like_0p5, 0.9), npt.NDArray[np.float64]
)
assert_type(
    random_st.noncentral_f(D_arr_0p1, D_arr_0p5, D_arr_0p9, size=1),
    npt.NDArray[np.float64],
)
assert_type(
    random_st.noncentral_f(D_arr_like_0p1, D_arr_like_0p5, D_arr_like_0p9, size=1),
    npt.NDArray[np.float64],
)

assert_type(random_st.binomial(10, 0.5), int)
assert_type(random_st.binomial(10, 0.5, size=None), int)
assert_type(random_st.binomial(10, 0.5, size=1), npt.NDArray[np.int_])
assert_type(random_st.binomial(I_arr_10, 0.5), npt.NDArray[np.int_])
assert_type(random_st.binomial(10, D_arr_0p5), npt.NDArray[np.int_])
assert_type(random_st.binomial(I_arr_10, 0.5, size=1), npt.NDArray[np.int_])
assert_type(random_st.binomial(10, D_arr_0p5, size=1), npt.NDArray[np.int_])
assert_type(random_st.binomial(I_arr_like_10, 0.5), npt.NDArray[np.int_])
assert_type(random_st.binomial(10, D_arr_like_0p5), npt.NDArray[np.int_])
assert_type(random_st.binomial(I_arr_10, D_arr_0p5), npt.NDArray[np.int_])
assert_type(random_st.binomial(I_arr_like_10, D_arr_like_0p5), npt.NDArray[np.int_])
assert_type(random_st.binomial(I_arr_10, D_arr_0p5, size=1), npt.NDArray[np.int_])
assert_type(
    random_st.binomial(I_arr_like_10, D_arr_like_0p5, size=1), npt.NDArray[np.int_]
)

assert_type(random_st.negative_binomial(10, 0.5), int)
assert_type(random_st.negative_binomial(10, 0.5, size=None), int)
assert_type(random_st.negative_binomial(10, 0.5, size=1), npt.NDArray[np.int_])
assert_type(random_st.negative_binomial(I_arr_10, 0.5), npt.NDArray[np.int_])
assert_type(random_st.negative_binomial(10, D_arr_0p5), npt.NDArray[np.int_])
assert_type(random_st.negative_binomial(I_arr_10, 0.5, size=1), npt.NDArray[np.int_])
assert_type(random_st.negative_binomial(10, D_arr_0p5, size=1), npt.NDArray[np.int_])
assert_type(random_st.negative_binomial(I_arr_like_10, 0.5), npt.NDArray[np.int_])
assert_type(random_st.negative_binomial(10, D_arr_like_0p5), npt.NDArray[np.int_])
assert_type(random_st.negative_binomial(I_arr_10, D_arr_0p5), npt.NDArray[np.int_])
assert_type(
    random_st.negative_binomial(I_arr_like_10, D_arr_like_0p5), npt.NDArray[np.int_]
)
assert_type(
    random_st.negative_binomial(I_arr_10, D_arr_0p5, size=1), npt.NDArray[np.int_]
)
assert_type(
    random_st.negative_binomial(I_arr_like_10, D_arr_like_0p5, size=1),
    npt.NDArray[np.int_],
)

assert_type(random_st.hypergeometric(20, 20, 10), int)
assert_type(random_st.hypergeometric(20, 20, 10, size=None), int)
assert_type(random_st.hypergeometric(20, 20, 10, size=1), npt.NDArray[np.int_])
assert_type(random_st.hypergeometric(I_arr_20, 20, 10), npt.NDArray[np.int_])
assert_type(random_st.hypergeometric(20, I_arr_20, 10), npt.NDArray[np.int_])
assert_type(
    random_st.hypergeometric(I_arr_20, 20, I_arr_like_10, size=1), npt.NDArray[np.int_]
)
assert_type(random_st.hypergeometric(20, I_arr_20, 10, size=1), npt.NDArray[np.int_])
assert_type(random_st.hypergeometric(I_arr_like_20, 20, I_arr_10), npt.NDArray[np.int_])
assert_type(random_st.hypergeometric(20, I_arr_like_20, 10), npt.NDArray[np.int_])
assert_type(random_st.hypergeometric(I_arr_20, I_arr_20, 10), npt.NDArray[np.int_])
assert_type(
    random_st.hypergeometric(I_arr_like_20, I_arr_like_20, 10), npt.NDArray[np.int_]
)
assert_type(
    random_st.hypergeometric(I_arr_20, I_arr_20, I_arr_10, size=1), npt.NDArray[np.int_]
)
assert_type(
    random_st.hypergeometric(I_arr_like_20, I_arr_like_20, I_arr_like_10, size=1),
    npt.NDArray[np.int_],
)

assert_type(random_st.randint(0, 100), int)
assert_type(random_st.randint(100), int)
assert_type(random_st.randint([100]), npt.NDArray[np.int_])
assert_type(random_st.randint(0, [100]), npt.NDArray[np.int_])

assert_type(random_st.randint(2, dtype=bool), bool)
assert_type(random_st.randint(0, 2, dtype=bool), bool)
assert_type(random_st.randint(I_bool_high_open, dtype=bool), npt.NDArray[np.bool_])
assert_type(
    random_st.randint(I_bool_low, I_bool_high_open, dtype=bool), npt.NDArray[np.bool_]
)
assert_type(random_st.randint(0, I_bool_high_open, dtype=bool), npt.NDArray[np.bool_])

assert_type(random_st.randint(2, dtype=np.bool_), bool)
assert_type(random_st.randint(0, 2, dtype=np.bool_), bool)
assert_type(random_st.randint(I_bool_high_open, dtype=np.bool_), npt.NDArray[np.bool_])
assert_type(
    random_st.randint(I_bool_low, I_bool_high_open, dtype=np.bool_),
    npt.NDArray[np.bool_],
)
assert_type(
    random_st.randint(0, I_bool_high_open, dtype=np.bool_), npt.NDArray[np.bool_]
)

assert_type(random_st.randint(256, dtype="u1"), int)
assert_type(random_st.randint(0, 256, dtype="u1"), int)
assert_type(random_st.randint(I_u1_high_open, dtype="u1"), npt.NDArray[np.uint8])
assert_type(
    random_st.randint(I_u1_low, I_u1_high_open, dtype="u1"), npt.NDArray[np.uint8]
)
assert_type(random_st.randint(0, I_u1_high_open, dtype="u1"), npt.NDArray[np.uint8])

assert_type(random_st.randint(256, dtype="uint8"), int)
assert_type(random_st.randint(0, 256, dtype="uint8"), int)
assert_type(random_st.randint(I_u1_high_open, dtype="uint8"), npt.NDArray[np.uint8])
assert_type(
    random_st.randint(I_u1_low, I_u1_high_open, dtype="uint8"), npt.NDArray[np.uint8]
)
assert_type(random_st.randint(0, I_u1_high_open, dtype="uint8"), npt.NDArray[np.uint8])

assert_type(random_st.randint(256, dtype=np.uint8), int)
assert_type(random_st.randint(0, 256, dtype=np.uint8), int)
assert_type(random_st.randint(I_u1_high_open, dtype=np.uint8), npt.NDArray[np.uint8])
assert_type(
    random_st.randint(I_u1_low, I_u1_high_open, dtype=np.uint8), npt.NDArray[np.uint8]
)
assert_type(random_st.randint(0, I_u1_high_open, dtype=np.uint8), npt.NDArray[np.uint8])

assert_type(random_st.randint(65536, dtype="u2"), int)
assert_type(random_st.randint(0, 65536, dtype="u2"), int)
assert_type(random_st.randint(I_u2_high_open, dtype="u2"), npt.NDArray[np.uint16])
assert_type(
    random_st.randint(I_u2_low, I_u2_high_open, dtype="u2"), npt.NDArray[np.uint16]
)
assert_type(random_st.randint(0, I_u2_high_open, dtype="u2"), npt.NDArray[np.uint16])

assert_type(random_st.randint(65536, dtype="uint16"), int)
assert_type(random_st.randint(0, 65536, dtype="uint16"), int)
assert_type(random_st.randint(I_u2_high_open, dtype="uint16"), npt.NDArray[np.uint16])
assert_type(
    random_st.randint(I_u2_low, I_u2_high_open, dtype="uint16"), npt.NDArray[np.uint16]
)
assert_type(
    random_st.randint(0, I_u2_high_open, dtype="uint16"), npt.NDArray[np.uint16]
)

assert_type(random_st.randint(65536, dtype=np.uint16), int)
assert_type(random_st.randint(0, 65536, dtype=np.uint16), int)
assert_type(random_st.randint(I_u2_high_open, dtype=np.uint16), npt.NDArray[np.uint16])
assert_type(
    random_st.randint(I_u2_low, I_u2_high_open, dtype=np.uint16), npt.NDArray[np.uint16]
)
assert_type(
    random_st.randint(0, I_u2_high_open, dtype=np.uint16), npt.NDArray[np.uint16]
)

assert_type(random_st.randint(4294967296, dtype="u4"), int)
assert_type(random_st.randint(0, 4294967296, dtype="u4"), int)
assert_type(random_st.randint(I_u4_high_open, dtype="u4"), npt.NDArray[np.uint32])
assert_type(
    random_st.randint(I_u4_low, I_u4_high_open, dtype="u4"), npt.NDArray[np.uint32]
)
assert_type(random_st.randint(0, I_u4_high_open, dtype="u4"), npt.NDArray[np.uint32])

assert_type(random_st.randint(4294967296, dtype="uint32"), int)
assert_type(random_st.randint(0, 4294967296, dtype="uint32"), int)
assert_type(random_st.randint(I_u4_high_open, dtype="uint32"), npt.NDArray[np.uint32])
assert_type(
    random_st.randint(I_u4_low, I_u4_high_open, dtype="uint32"), npt.NDArray[np.uint32]
)
assert_type(
    random_st.randint(0, I_u4_high_open, dtype="uint32"), npt.NDArray[np.uint32]
)

assert_type(random_st.randint(4294967296, dtype=np.uint32), int)
assert_type(random_st.randint(0, 4294967296, dtype=np.uint32), int)
assert_type(random_st.randint(I_u4_high_open, dtype=np.uint32), npt.NDArray[np.uint32])
assert_type(
    random_st.randint(I_u4_low, I_u4_high_open, dtype=np.uint32), npt.NDArray[np.uint32]
)
assert_type(
    random_st.randint(0, I_u4_high_open, dtype=np.uint32), npt.NDArray[np.uint32]
)

assert_type(random_st.randint(4294967296, dtype=np.uint), int)
assert_type(random_st.randint(0, 4294967296, dtype=np.uint), int)
assert_type(random_st.randint(I_u4_high_open, dtype=np.uint), npt.NDArray[np.uint])
assert_type(
    random_st.randint(I_u4_low, I_u4_high_open, dtype=np.uint), npt.NDArray[np.uint]
)
assert_type(random_st.randint(0, I_u4_high_open, dtype=np.uint), npt.NDArray[np.uint])

assert_type(random_st.randint(18446744073709551616, dtype="u8"), int)
assert_type(random_st.randint(0, 18446744073709551616, dtype="u8"), int)
assert_type(random_st.randint(I_u8_high_open, dtype="u8"), npt.NDArray[np.uint64])
assert_type(
    random_st.randint(I_u8_low, I_u8_high_open, dtype="u8"), npt.NDArray[np.uint64]
)
assert_type(random_st.randint(0, I_u8_high_open, dtype="u8"), npt.NDArray[np.uint64])

assert_type(random_st.randint(18446744073709551616, dtype="uint64"), int)
assert_type(random_st.randint(0, 18446744073709551616, dtype="uint64"), int)
assert_type(random_st.randint(I_u8_high_open, dtype="uint64"), npt.NDArray[np.uint64])
assert_type(
    random_st.randint(I_u8_low, I_u8_high_open, dtype="uint64"), npt.NDArray[np.uint64]
)
assert_type(
    random_st.randint(0, I_u8_high_open, dtype="uint64"), npt.NDArray[np.uint64]
)

assert_type(random_st.randint(18446744073709551616, dtype=np.uint64), int)
assert_type(random_st.randint(0, 18446744073709551616, dtype=np.uint64), int)
assert_type(random_st.randint(I_u8_high_open, dtype=np.uint64), npt.NDArray[np.uint64])
assert_type(
    random_st.randint(I_u8_low, I_u8_high_open, dtype=np.uint64), npt.NDArray[np.uint64]
)
assert_type(
    random_st.randint(0, I_u8_high_open, dtype=np.uint64), npt.NDArray[np.uint64]
)

assert_type(random_st.randint(128, dtype="i1"), int)
assert_type(random_st.randint(-128, 128, dtype="i1"), int)
assert_type(random_st.randint(I_i1_high_open, dtype="i1"), npt.NDArray[np.int8])
assert_type(
    random_st.randint(I_i1_low, I_i1_high_open, dtype="i1"), npt.NDArray[np.int8]
)
assert_type(random_st.randint(-128, I_i1_high_open, dtype="i1"), npt.NDArray[np.int8])

assert_type(random_st.randint(128, dtype="int8"), int)
assert_type(random_st.randint(-128, 128, dtype="int8"), int)
assert_type(random_st.randint(I_i1_high_open, dtype="int8"), npt.NDArray[np.int8])
assert_type(
    random_st.randint(I_i1_low, I_i1_high_open, dtype="int8"), npt.NDArray[np.int8]
)
assert_type(random_st.randint(-128, I_i1_high_open, dtype="int8"), npt.NDArray[np.int8])

assert_type(random_st.randint(128, dtype=np.int8), int)
assert_type(random_st.randint(-128, 128, dtype=np.int8), int)
assert_type(random_st.randint(I_i1_high_open, dtype=np.int8), npt.NDArray[np.int8])
assert_type(
    random_st.randint(I_i1_low, I_i1_high_open, dtype=np.int8), npt.NDArray[np.int8]
)
assert_type(
    random_st.randint(-128, I_i1_high_open, dtype=np.int8), npt.NDArray[np.int8]
)

assert_type(random_st.randint(32768, dtype="i2"), int)
assert_type(random_st.randint(-32768, 32768, dtype="i2"), int)
assert_type(random_st.randint(I_i2_high_open, dtype="i2"), npt.NDArray[np.int16])
assert_type(
    random_st.randint(I_i2_low, I_i2_high_open, dtype="i2"), npt.NDArray[np.int16]
)
assert_type(
    random_st.randint(-32768, I_i2_high_open, dtype="i2"), npt.NDArray[np.int16]
)
assert_type(random_st.randint(32768, dtype="int16"), int)
assert_type(random_st.randint(-32768, 32768, dtype="int16"), int)
assert_type(random_st.randint(I_i2_high_open, dtype="int16"), npt.NDArray[np.int16])
assert_type(
    random_st.randint(I_i2_low, I_i2_high_open, dtype="int16"), npt.NDArray[np.int16]
)
assert_type(
    random_st.randint(-32768, I_i2_high_open, dtype="int16"), npt.NDArray[np.int16]
)
assert_type(random_st.randint(32768, dtype=np.int16), int)
assert_type(random_st.randint(-32768, 32768, dtype=np.int16), int)
assert_type(random_st.randint(I_i2_high_open, dtype=np.int16), npt.NDArray[np.int16])
assert_type(
    random_st.randint(I_i2_low, I_i2_high_open, dtype=np.int16), npt.NDArray[np.int16]
)
assert_type(
    random_st.randint(-32768, I_i2_high_open, dtype=np.int16), npt.NDArray[np.int16]
)

assert_type(random_st.randint(2147483648, dtype="i4"), int)
assert_type(random_st.randint(-2147483648, 2147483648, dtype="i4"), int)
assert_type(random_st.randint(I_i4_high_open, dtype="i4"), npt.NDArray[np.int32])
assert_type(
    random_st.randint(I_i4_low, I_i4_high_open, dtype="i4"), npt.NDArray[np.int32]
)
assert_type(
    random_st.randint(-2147483648, I_i4_high_open, dtype="i4"), npt.NDArray[np.int32]
)

assert_type(random_st.randint(2147483648, dtype="int32"), int)
assert_type(random_st.randint(-2147483648, 2147483648, dtype="int32"), int)
assert_type(random_st.randint(I_i4_high_open, dtype="int32"), npt.NDArray[np.int32])
assert_type(
    random_st.randint(I_i4_low, I_i4_high_open, dtype="int32"), npt.NDArray[np.int32]
)
assert_type(
    random_st.randint(-2147483648, I_i4_high_open, dtype="int32"), npt.NDArray[np.int32]
)

assert_type(random_st.randint(2147483648, dtype=np.int32), int)
assert_type(random_st.randint(-2147483648, 2147483648, dtype=np.int32), int)
assert_type(random_st.randint(I_i4_high_open, dtype=np.int32), npt.NDArray[np.int32])
assert_type(
    random_st.randint(I_i4_low, I_i4_high_open, dtype=np.int32), npt.NDArray[np.int32]
)
assert_type(
    random_st.randint(-2147483648, I_i4_high_open, dtype=np.int32),
    npt.NDArray[np.int32],
)

assert_type(random_st.randint(2147483648, dtype=np.int_), int)
assert_type(random_st.randint(-2147483648, 2147483648, dtype=np.int_), int)
assert_type(random_st.randint(I_i4_high_open, dtype=np.int_), npt.NDArray[np.int_])
assert_type(
    random_st.randint(I_i4_low, I_i4_high_open, dtype=np.int_), npt.NDArray[np.int_]
)
assert_type(
    random_st.randint(-2147483648, I_i4_high_open, dtype=np.int_), npt.NDArray[np.int_]
)

assert_type(random_st.randint(9223372036854775808, dtype="i8"), int)
assert_type(
    random_st.randint(-9223372036854775808, 9223372036854775808, dtype="i8"), int
)
assert_type(random_st.randint(I_i8_high_open, dtype="i8"), npt.NDArray[np.int64])
assert_type(
    random_st.randint(I_i8_low, I_i8_high_open, dtype="i8"), npt.NDArray[np.int64]
)
assert_type(
    random_st.randint(-9223372036854775808, I_i8_high_open, dtype="i8"),
    npt.NDArray[np.int64],
)

assert_type(random_st.randint(9223372036854775808, dtype="int64"), int)
assert_type(
    random_st.randint(-9223372036854775808, 9223372036854775808, dtype="int64"), int
)
assert_type(random_st.randint(I_i8_high_open, dtype="int64"), npt.NDArray[np.int64])
assert_type(
    random_st.randint(I_i8_low, I_i8_high_open, dtype="int64"), npt.NDArray[np.int64]
)
assert_type(
    random_st.randint(-9223372036854775808, I_i8_high_open, dtype="int64"),
    npt.NDArray[np.int64],
)

assert_type(random_st.randint(9223372036854775808, dtype=np.int64), int)
assert_type(
    random_st.randint(-9223372036854775808, 9223372036854775808, dtype=np.int64), int
)
assert_type(random_st.randint(I_i8_high_open, dtype=np.int64), npt.NDArray[np.int64])
assert_type(
    random_st.randint(I_i8_low, I_i8_high_open, dtype=np.int64), npt.NDArray[np.int64]
)
assert_type(
    random_st.randint(-9223372036854775808, I_i8_high_open, dtype=np.int64),
    npt.NDArray[np.int64],
)

assert_type(random_st._bit_generator, np.random.BitGenerator)

assert_type(random_st.bytes(2), bytes)

assert_type(random_st.choice(5), int)
assert_type(random_st.choice(5, 3), npt.NDArray[np.int_])
assert_type(random_st.choice(5, 3, replace=True), npt.NDArray[np.int_])
assert_type(random_st.choice(5, 3, p=[1 / 5] * 5), npt.NDArray[np.int_])
assert_type(random_st.choice(5, 3, p=[1 / 5] * 5, replace=False), npt.NDArray[np.int_])

assert_type(random_st.choice(["pooh", "rabbit", "piglet", "Christopher"]), Any)
assert_type(
    random_st.choice(["pooh", "rabbit", "piglet", "Christopher"], 3),
    np.ndarray[Any, Any],
)
assert_type(
    random_st.choice(["pooh", "rabbit", "piglet", "Christopher"], 3, p=[1 / 4] * 4),
    np.ndarray[Any, Any],
)
assert_type(
    random_st.choice(["pooh", "rabbit", "piglet", "Christopher"], 3, replace=True),
    np.ndarray[Any, Any],
)
assert_type(
    random_st.choice(
        ["pooh", "rabbit", "piglet", "Christopher"],
        3,
        replace=False,
        p=np.array([1 / 8, 1 / 8, 1 / 2, 1 / 4]),
    ),
    np.ndarray[Any, Any],
)

assert_type(random_st.dirichlet([0.5, 0.5]), npt.NDArray[np.float64])
assert_type(random_st.dirichlet(np.array([0.5, 0.5])), npt.NDArray[np.float64])
assert_type(random_st.dirichlet(np.array([0.5, 0.5]), size=3), npt.NDArray[np.float64])

assert_type(random_st.multinomial(20, [1 / 6.0] * 6), npt.NDArray[np.int_])
assert_type(random_st.multinomial(20, np.array([0.5, 0.5])), npt.NDArray[np.int_])
assert_type(random_st.multinomial(20, [1 / 6.0] * 6, size=2), npt.NDArray[np.int_])

assert_type(random_st.multivariate_normal([0.0], [[1.0]]), npt.NDArray[np.float64])
assert_type(
    random_st.multivariate_normal([0.0], np.array([[1.0]])), npt.NDArray[np.float64]
)
assert_type(
    random_st.multivariate_normal(np.array([0.0]), [[1.0]]), npt.NDArray[np.float64]
)
assert_type(
    random_st.multivariate_normal([0.0], np.array([[1.0]])), npt.NDArray[np.float64]
)

assert_type(random_st.permutation(10), npt.NDArray[np.int_])
assert_type(random_st.permutation([1, 2, 3, 4]), np.ndarray[Any, Any])
assert_type(random_st.permutation(np.array([1, 2, 3, 4])), np.ndarray[Any, Any])
assert_type(random_st.permutation(D_2D), np.ndarray[Any, Any])

assert_type(random_st.shuffle(np.arange(10)), None)
assert_type(random_st.shuffle([1, 2, 3, 4, 5]), None)
assert_type(random_st.shuffle(D_2D), None)

assert_type(np.random.RandomState(pcg64), np.random.RandomState)
assert_type(np.random.RandomState(0), np.random.RandomState)
assert_type(np.random.RandomState([0, 1, 2]), np.random.RandomState)
assert_type(random_st.__str__(), str)
assert_type(random_st.__repr__(), str)
random_st_state = random_st.__getstate__()
assert_type(random_st_state, dict[str, Any])
assert_type(random_st.__setstate__(random_st_state), None)
assert_type(random_st.seed(), None)
assert_type(random_st.seed(1), None)
assert_type(random_st.seed([0, 1]), None)
random_st_get_state = random_st.get_state()
assert_type(random_st_state, dict[str, Any])
random_st_get_state_legacy = random_st.get_state(legacy=True)
assert_type(
    random_st_get_state_legacy,
    dict[str, Any] | tuple[str, npt.NDArray[np.uint32], int, int, float],
)
assert_type(random_st.set_state(random_st_get_state), None)

assert_type(random_st.rand(), float)
assert_type(random_st.rand(1), npt.NDArray[np.float64])
assert_type(random_st.rand(1, 2), npt.NDArray[np.float64])
assert_type(random_st.randn(), float)
assert_type(random_st.randn(1), npt.NDArray[np.float64])
assert_type(random_st.randn(1, 2), npt.NDArray[np.float64])
assert_type(random_st.random_sample(), float)
assert_type(random_st.random_sample(1), npt.NDArray[np.float64])
assert_type(random_st.random_sample(size=(1, 2)), npt.NDArray[np.float64])

assert_type(random_st.tomaxint(), int)
assert_type(random_st.tomaxint(1), npt.NDArray[np.int_])
assert_type(random_st.tomaxint((1,)), npt.NDArray[np.int_])

assert_type(np.random.set_bit_generator(pcg64), None)
assert_type(np.random.get_bit_generator(), np.random.BitGenerator)
