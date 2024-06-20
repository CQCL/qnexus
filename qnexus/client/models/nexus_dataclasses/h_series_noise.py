"""Validation classes for H series noise models."""
from typing import Optional

from pydantic import BaseModel


class UserErrorParams(BaseModel):
    """User provided error values that override machine values.

    See the emulator device sheets for details of each parameter.
    """

    # Physical Noise
    p1: Optional[float] = None
    p2: Optional[float] = None
    p_meas: Optional[float] = None
    p_init: Optional[float] = None
    p_crosstalk_meas: Optional[float] = None
    p_crosstalk_init: Optional[float] = None
    p1_emission_ratio: Optional[float] = None
    p2_emission_ratio: Optional[float] = None
    # Dephasing Noise
    quadratic_dephasing_rate: Optional[float] = None
    linear_dephasing_rate: Optional[float] = None
    coherent_to_incoherent_factor: Optional[float] = None
    coherent_dephasing: Optional[bool] = None
    transport_dephasing: Optional[bool] = None
    idle_dephasing: Optional[bool] = None
    # Arbitrary Angle Noise Scaling
    przz_a: Optional[float] = None
    przz_b: Optional[float] = None
    przz_c: Optional[float] = None
    przz_d: Optional[float] = None
    przz_power: Optional[float] = None
    # Scaling
    scale: Optional[float] = None
    p1_scale: Optional[float] = None
    p2_scale: Optional[float] = None
    meas_scale: Optional[float] = None
    init_scale: Optional[float] = None
    memory_scale: Optional[float] = None
    emission_scale: Optional[float] = None
    crosstalk_scale: Optional[float] = None
    leakage_scale: Optional[float] = None
