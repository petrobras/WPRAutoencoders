import numpy as np
import matplotlib.pyplot as plt
import scipy.special as sc
from Stehfest import Stehfest
from Utilities import calc_derivative

def lap_pwd(u, cd, s):
    """
    Calculate the Pwd for a given skin and storage in the Laplace domain

    Keyword arguments:
    u -- Laplace variable
    cd -- storage coefficient
    s -- skin value
    """
    num = sc.kn(0, np.sqrt(u))
    den = u * (1 + u*cd*(num + s))
    return num/den

def calc_press(time, k, phi, h, ct, B, mu, q, s, c, rw):
    """
    Calculate the pressure result for a well inside an infinite 
    reservoir with storage

    Keyword arguments:
    time -- array of time measurements
    k -- permeability in md
    phi -- porosity between 0 and 1
    h -- reservoir height in m
    ct -- total compressibility in cm2/kgf
    B -- volume formation factor
    mu -- fluid viscosity in cp
    q -- fluid rate in m3/d
    s -- skin value
    c -- storage value
    rw -- well radius in m
    """

    factor = 19.03 * q * B * mu / (k * h)
    cd = c / (2 * np.pi * rw**2 * phi * h * ct)
    const = 0.0003484 * k / (phi * mu * ct * rw**2)
    stehfest = Stehfest(16)
    return factor * stehfest.run(const*time, lap_pwd, cd, s)

def main():
    time = np.logspace(-1, 3)

    dp1 = calc_press(time, 10, 0.2, 50, 1e-5, 1, 1, 200, 0, 0.1, 0.108)
    dp2 = calc_press(time, 10, 0.2, 50, 1e-5, 1, 1, 200, 20, 0.1, 0.108)

    der_dp1 = calc_derivative(time, dp1, 0.0)
    der_dp2 = calc_derivative(time, dp2, 0.0)

    fig, ax = plt.subplots(1,1)
    ax.plot(time[1:-1], dp1[1:-1], ".")
    ax.plot(time[1:-1], dp2[1:-1], ".")
    ax.plot(time[1:-1], der_dp1[1:-1], ".")
    ax.plot(time[1:-1], der_dp2[1:-1], ".")
    ax.set_xscale("log")
    ax.set_yscale("log")
    plt.show()

if __name__ == "__main__":
    main()