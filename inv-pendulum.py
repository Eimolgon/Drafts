import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Parameters
g = 9.81
m_cart = 1
m_pend = 1
l = 1
k = 1
c = 1

F = 1
I = (m_pend * l**2) / 12

