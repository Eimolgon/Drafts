import numpy as np
import matplotlib.pyplot as plt

# Parameters (https://www.bilenky.com/tandem-specs)

g = 9.81
lb2kg = 0.453592
in2m = 0.0254

m1 = 80                 # Rider 1 mass
m2 = 80                 # Rider 2 mass
b1 = 0.3
b2 = 0.9
h1 = 0.9
h2 = h1

mb = 40 * lb2kg          # lb to kg
mt = m1 + m2 + mb
w = 68.5 * in2m          # inch to m
Rr = (26 * in2m)/2
mux = 0.6

b = (m1 * b1 + m2 * b2)/mt
h = (m1 * h1 + m2 * h2)/mt

# Wheelie limit force
Xr = (b * mt * g)/h
Tr = Xr * Rr 

# Grip limit force
Xrg = ((w - b)/(w - mux * h))* mux * mt * g

print('Minimum Rear Wheel Force for Wheelie: %2.2f [N]' % (Xr))
print('Required Rear wheel torque: %2.2f [Nm]' % (Tr))
print('Maximum allowable rear wheel force for grip: %2.2f ' % (Xrg))
