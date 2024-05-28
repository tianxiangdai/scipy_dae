import numpy as np
from scipy.linalg import eig, hessenberg, orth

def RadauIIA(s):
    # solve zeros of Radau polynomial, see Hairer1999 (7)
    from numpy.polynomial import Polynomial as P

    poly = P([0, 1]) ** (s - 1) * P([-1, 1]) ** s
    poly_der = poly.deriv(s - 1)
    c = poly_der.roots()

    # compute coefficients a_ij, see Hairer1999 (11)
    A = np.zeros((s, s), dtype=float)
    for i in range(s):
        Mi = np.zeros((s, s), dtype=float)
        ri = np.zeros(s, dtype=float)
        for q in range(s):
            Mi[q] = c**q
            ri[q] = c[i] ** (q + 1) / (q + 1)
        A[i] = np.linalg.solve(Mi, ri)

    b = A[-1, :]
    p = 2 * s - 1
    return A, b, c, p

gamma = 3 + 3 ** (2 / 3) - 3 ** (1 / 3)
alpha = 3 + 0.5 * (3 ** (1 / 3) - 3 ** (2 / 3))
beta = 0.5 * (3 ** (5 / 6) + 3 ** (7 / 6))

s = 3
A, b, c, p = RadauIIA(s)
print(f"A:\n{A}")

A_inv = np.linalg.inv(A)
print(f"A_inv:\n{A_inv}")
print(f"A_inv @ A:\n{A_inv @ A}")
# exit()

H, Q = hessenberg(A_inv, calc_q=True)
# TODO: hessenberg form seems to be not necessary!
H, Q = A_inv, np.eye(s)
print(f"H:\n{H}")
print(f"Q:\n{Q}")
print(f"A_inv = Q @ H @ Q.T:\n{Q @ H @ Q.T}")
print(f"A_inv - Q @ H @ Q.T:\n{A_inv - Q @ H @ Q.T}")
print(f"Q.T @ Q:\n{Q.T @ Q}")
# exit()

lambdas, V = eig(H)

# scale eigenvectors to get a "nice" transformation matrix
# TODO: This gives the best results in Radau method
for i in range(s):
    V[:, i] /= V[-1, i]
# # normalize eigenvectors
# V /= np.linalg.norm(V, axis=0)

V_inv = np.linalg.inv(V)
Lambdas = np.diag(lambdas)
print(f"Lambdas:\n{Lambdas}")
print(f"V:\n{V}")
H_reconstructed = V @ Lambdas @ V_inv
H_reconstructed = H_reconstructed.real # prune zero imaginary parts
print(f"H = V @ Lambdas @ V_inv:\n{H_reconstructed}")
print(f"H - V @ Lambdas @ V_inv:\n{H - H_reconstructed}")
# exit()

P = np.array([
    [1j, -1j, 0],
    [1, 1, 0],
    [0, 0, 1]
])
P_inv = np.linalg.inv(P)
Lambdas_real = P @ Lambdas @ P_inv
Lambdas_real = Lambdas_real.real # prune zero imaginary parts
print(f"P:\n{P}")
print(f"P_inv:\n{P_inv}")
print(f"Lambdas_real:\n{Lambdas_real}")
print(f"Lambdas - P_inv @ Lambdas_real @ P:\n{Lambdas - P_inv @ Lambdas_real @ P}")
# exit()

# fortran/ julia ordering
R = np.array([
    [0, 0, 1],
    [1, 0, 0],
    [0, 1, 0]
])
# scipy ordering
R = np.array([
    [0, 0, 1],
    [1, 0, 0],
    [0, -1, 0]
])
# R = np.eye(3)

Mus = R @ Lambdas_real @ R.T
print(f"Mus:\n{Mus}")
print(f"Lambdas_real - R.T @ Mus @ R:\n{Lambdas_real - R.T @ Mus @ R}")
# exit()

T = Q @ V @ P_inv @ R.T
T = T.real # prune zero imaginary parts
# T[:, 0] /= T[-1, 0]
# T[:, 1] /= T[0, 1]
# T[:, 2] /= T[-1, 2]
T_inv = np.linalg.inv(T)
Mus2 = T_inv @ A_inv @ T
Mus2 = Mus2.real # prune zero imaginary parts
print(f"Mus2:\n{Mus2}")
np.set_printoptions(20)
print(f"T:\n{T}")
# print(f"T_inv:\n{T_inv}")
exit()

# radau.py
T_scipy = np.array([
    [0.09443876248897524, -0.14125529502095421, 0.03002919410514742],
    [0.25021312296533332, 0.20412935229379994, -0.38294211275726192],
    [1, 1, 0]])
TI_scipy = np.array([
    [4.17871859155190428, 0.32768282076106237, 0.52337644549944951],
    [-4.17871859155190428, -0.32768282076106237, 0.47662355450055044],
    [0.50287263494578682, -2.57192694985560522, 0.59603920482822492]])
print(f"T_scipy:\n{T_scipy}")

# radau5.f
T11=9.12323948708929427920e-02
T12=-0.1412552950209542084e+00
T13=-3.0029194105147424492e-02
T21=0.24171793270710701896e+00
T22=0.20412935229379993199e+00
T23=0.38294211275726193779e+00
T31=0.96604818261509293619e+00

# # firk_tableaus.jl, 
# # see https://github.com/SciML/OrdinaryDiffEq.jl/blob/1e8716a6cc2c334ff96049ab781f0aef10fba328/src/tableaus/firk_tableaus.jl#L2
# T11 = 9.1232394870892942792e-02
# T12 = -0.14125529502095420843e0
# T13 = -3.0029194105147424492e-02
# T21 = 0.24171793270710701896e0
# T22 = 0.20412935229379993199e0
# T23 = 0.38294211275726193779e0
# T31 = 0.96604818261509293619e0

T_fortran_julia = np.array([
    [T11, T12, T13],
    [T21, T22, T23],
    [T31, 1.0, 0.0],
], dtype=float)
TI_fortran_julia = np.linalg.inv(T_fortran_julia)
print(f"T_fortran_julia:\n{T_fortran_julia}")

gamma = 3 + 3 ** (2 / 3) - 3 ** (1 / 3)
alpha = 3 + 0.5 * (3 ** (1 / 3) - 3 ** (2 / 3))
beta = 0.5 * (3 ** (5 / 6) + 3 ** (7 / 6))
Mus_fortran_julia = np.array([
    [gamma, 0, 0],
    [0, alpha, -beta],
    [0, beta, alpha],
])
Mus_scipy = np.array([
    [gamma, 0, 0],
    [0, alpha, beta],
    [0, -beta, alpha],
])
# print(f"Mus_fortran_julia:\n{Mus_fortran_julia}")
# print(f"TI_fortran_julia @ A_inv @ T_fortran_julia:\n{TI_fortran_julia @ A_inv @ T_fortran_julia}")
error_fortran_julia = np.linalg.norm(Mus_fortran_julia - TI_fortran_julia @ A_inv @ T_fortran_julia)
print(f"error_fortran_julia: {error_fortran_julia}")

# print(f"Mus_scipy:\n{Mus_scipy}")
# print(f"TI_scipy @ A_inv @ T:\n{TI_scipy @ A_inv @ T_scipy}")
error_scipy = np.linalg.norm(Mus_scipy - TI_scipy @ A_inv @ T_scipy)
print(f"error_scipy: {error_scipy}")

exit()

# A_inv_reconstructed = vl @ np.diag(w) @ np.linalg.inv(vl)
# A_inv_reconstructed = A_inv_reconstructed.real # remove zero imaginary parts
# print(f"A_inv_reconstructed:\n{A_inv_reconstructed}")
# print(f"A_inv - A_inv_reconstructed:\n{A_inv - A_inv_reconstructed}")

# T = np.array([
#     [0, 0, 1],
#     [1, 1, 0],
#     [1j, -1j, 0],
# ])
# T_inv = np.linalg.inv(T)
# print(f"T:\n{T}")
# print(f"T_inv:\n{T_inv}")

# tmp = T @ vl @ np.diag(w) @ np.linalg.inv(vl) @ T_inv

# T_new = T @ vl
# T_new_inv = np.linalg.inv(T_new)
# print(f"T_new:\n{T_new}")
# print(f"T_new_inv:\n{T_new_inv}")

T = np.array([
    [0.09443876248897524, -0.14125529502095421, 0.03002919410514742],
    [0.25021312296533332, 0.20412935229379994, -0.38294211275726192],
    [1, 1, 0],
])
TI = np.array([
    [4.17871859155190428, 0.32768282076106237, 0.52337644549944951],
    [-4.17871859155190428, -0.32768282076106237, 0.47662355450055044],
    [0.50287263494578682, -2.57192694985560522, 0.59603920482822492],
])
T_inv = np.linalg.inv(T)
print(f"T:\n{T}")
print(f"TI:\n{TI}")
print(f"T_inv:\n{T_inv}")

# print(f"{T @ A_inv @ np.linalg.inv(T)}")
MUS_real = np.linalg.inv(T) @ A_inv @ T
print(f"np.linalg.inv(T) @ A_inv @ T:\n{MUS_real}")
# print(f"{T @ A @ np.linalg.inv(T)}")
# print(f"{np.linalg.inv(T) @ A @ T}")

# Eigendecomposition of A is done: A = T L T**-1. There is 1 real eigenvalue
# and a complex conjugate pair. They are written below.
MU_REAL = 3 + 3 ** (2 / 3) - 3 ** (1 / 3)
MU_COMPLEX1 = (3 + 0.5 * (3 ** (1 / 3) - 3 ** (2 / 3))
              + 0.5j * (3 ** (5 / 6) + 3 ** (7 / 6)))
MU_COMPLEX2 = (3 + 0.5 * (3 ** (1 / 3) - 3 ** (2 / 3))
              - 0.5j * (3 ** (5 / 6) + 3 ** (7 / 6)))
# print(f"{MU_REAL= }")
# print(f"{MU_COMPLEX1= }")
# print(f"{MU_COMPLEX2= }")

# MUS = np.array([MU_REAL, MU_COMPLEX1, MU_COMPLEX2])
MUS = np.array([MU_COMPLEX1, MU_COMPLEX2, MU_REAL])
print(f"MUS:\n{MUS}")

P = np.array([
    [0, 0, 1],
    [1, 1, 0],
    [1j, -1j, 0],
])
# MUS_real = np.linalg.inv(P) @ np.diag(MUS) @ P
MUS_real = P @ np.diag(MUS) @ np.linalg.inv(P)
print(f"MUS_real:\n{MUS_real}")

print(f"A_inv = T @ MUS_real @ np.linalg.inv(T):\n{T @ MUS_real @ np.linalg.inv(T)}")


# print(f"{T @ np.eye(3)}")
# v1 = null_space(A_inv - MU_REAL * np.eye(s))
# v2 = null_space(A_inv - MU_COMPLEX1 * np.eye(s))
# v3 = np.linalg.solve(A_inv - MU_COMPLEX2 * np.eye(s), v2)
# print(f"v1:\n{v1}")
# print(f"v2:\n{v2}")
# print(f"v3:\n{v3}")
# V = np.hstack((v1, v2, v3))
# print(f"V:\n{V}")

# A_inv_reconstructed = V @ np.diag(MUS) @ np.linalg.inv(V)
# # A_inv_reconstructed = A_inv_reconstructed.real # remove zero imaginary parts
# print(f"{A_inv_reconstructed}")



# T, Z = schur(A_inv, output="real")
# # T, Z = rsf2csf(T, Z)
# print(f"Z:\n{Z}")
# print(f"T:\n{T}")