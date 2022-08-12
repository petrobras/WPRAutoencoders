import matplotlib.pyplot as plt
import numpy as np
from scipy.special import expi

from Utilities import calc_derivative

class WPRGenerator:
    def __init__(self, tk, k, por, h, ct, Bo, visc, q, skin, L1, L2, L3, L4, rw, n_grids=41):
        self.tk = tk
        self.k = k
        self.por = por
        self.h = h
        self.ct = ct
        self.Bo = Bo
        self.visc = visc
        self.q = q
        self.skin = skin
        self.n_grids = n_grids
        self.L1 = L1
        self.L2 = L2
        self.L3 = L3
        self.L4 = L4
        self.rw = rw
        self.matrix_d = np.zeros((self.n_grids, self.n_grids))
        self.center = int((self.n_grids - 1) / 2)
        self.index = np.linspace(1, self.center, self.center)
        self.setup_matrix_d()
            
    def setup_matrix_d(self):
        self.matrix_d[self.center, self.center] = self.rw
        self.fill_center_up()
        self.fill_center_down()
        self.fill_center_right()
        self.fill_center_left()
        self.fill_northeast()
        self.fill_northwest()
        self.fill_southwest()
        self.fill_southeast()

    def fill_center_up(self):
        for i in self.index:
            k_up = int(self.center - i)
            if i % 2 == 0:
                self.matrix_d[k_up, self.center] = i * self.L1 + i * self.L3
            else:
                self.matrix_d[k_up, self.center] = (i + 1) * self.L1 + (i - 1) * self.L3

    def fill_center_down(self):
        for i in self.index:
            k_down = int(self.center + i)
            if i % 2 == 0:
                self.matrix_d[k_down, self.center] = i * self.L1 + i * self.L3
            else:
                self.matrix_d[k_down, self.center] = (i - 1) * self.L1 + (i + 1) * self.L3

    def fill_center_right(self):
        for i in self.index:
            k_right = int(self.center + i)
            if i % 2 == 0:
                self.matrix_d[self.center, k_right] = i * self.L4 + i * self.L2
            else:
                self.matrix_d[self.center, k_right] = (i + 1) * self.L4 + (i - 1) * self.L2

    def fill_center_left(self):
        for i in self.index:
            k_left = int(self.center - i)
            if i % 2 == 0:
                self.matrix_d[self.center, k_left] = i * self.L4 + i * self.L2
            else:
                self.matrix_d[self.center, k_left] = (i - 1) * self.L4 + (i + 1) * self.L2

    def fill_northeast(self):
        for i in self.index:
            for j in self.index:
                i = int(i)
                j = int(j)
                self.matrix_d[i - 1, int(self.center + j)] = np.sqrt(
                    self.matrix_d[i - 1, int(self.center)] ** 2
                    + self.matrix_d[int(self.center), int(self.center + j)] ** 2
                )

    def fill_southeast(self):
        for i in self.index:
            for j in self.index:
                i = int(i)
                j = int(j)
                self.matrix_d[int(self.center + i), int(self.center + j)] = np.sqrt(
                    self.matrix_d[int(self.center + i), int(self.center)] ** 2
                    + self.matrix_d[int(self.center), int(self.center + j)] ** 2
                )

    def fill_northwest(self):
        for i in self.index:
            for j in self.index:
                i = int(i)
                j = int(j)
                self.matrix_d[i - 1, j - 1] = np.sqrt(
                    self.matrix_d[i - 1, int(self.center)] ** 2 + self.matrix_d[int(self.center), j - 1] ** 2
                )

    def fill_southwest(self):
        for i in self.index:
            for j in self.index:
                i = int(i)
                j = int(j)
                self.matrix_d[int(self.center + i), j - 1] = np.sqrt(
                    self.matrix_d[int(self.center + i), int(self.center)] ** 2
                    + self.matrix_d[int(self.center), j - 1] ** 2
                )


    def calc_dp(self, t):
        kp = 19.03 * self.q * self.Bo * self.visc / (self.k * self.h)
        matrix_p = np.zeros((self.n_grids, self.n_grids))

        for i in range(self.n_grids):
            for j in range(self.n_grids):
                matrix_p[i, j] = (
                    0.5
                    * kp
                    * -expi(
                        -(0.25 * self.por * self.visc * self.ct * self.matrix_d[i, j] ** 2)
                        / (0.0003484 * self.k * t)
                    )
                )
        matrix_p[self.center, self.center] = kp * (
            -0.5
            * expi(
                -(0.25 * self.por * self.visc * self.ct * self.matrix_d[self.center, self.center] ** 2)
                / (0.0003484 * self.k * t)
            )
            + self.skin
        )
        return np.sum(matrix_p)

    def create_dpu(self):
        return np.array([self.calc_dp(t) for t in self.tk])


def main():
    k = 1000
    por = 0.2
    h = 50
    ct = 1e-5
    Bo = 1
    visc = 1
    pi = 100
    skin = 0
    model = "infinite"
    L1, L2, L3, L4 = (300, 1000000, 1000000, 1000000)
    rw = 0.108
    q_ref = 15.9

    tk = np.logspace(-2,3,20)
    case_1 = WPRGenerator(tk, k, por, h, ct, Bo, visc, q_ref, skin, L1, L2, L3, L4, rw)
    case_2 = WPRGenerator(tk, k, por, h, ct, Bo, visc, q_ref, 10, L1, L2, L3, L4, rw)
    case_3 = WPRGenerator(tk, k, por, h, ct, Bo, visc, q_ref, -2, L1, L2, L3, L4, rw)
    dp_u_1 = case_1.create_dpu()
    dp_u_2 = case_2.create_dpu()
    dp_u_3 = case_3.create_dpu()
    # print(dp_u)
    der_u_1 = calc_derivative(tk, dp_u_1, 0.0)
    der_u_2 = calc_derivative(tk, dp_u_2, 0.0)
    der_u_3 = calc_derivative(tk, dp_u_3, 0.0)
    plt.loglog(tk[1:-1], dp_u_1[1:-1], label="dp1")
    plt.loglog(tk[1:-1], der_u_1[1:-1], label="der1")
    plt.loglog(tk[1:-1], dp_u_2[1:-1], label="dp2")
    plt.loglog(tk[1:-1], der_u_2[1:-1], label="der2")
    plt.loglog(tk[1:-1], dp_u_3[1:-1], label="dp3")
    plt.loglog(tk[1:-1], der_u_3[1:-1], label="der3")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()