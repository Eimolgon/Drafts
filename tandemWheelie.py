import numpy as np
import matplotlib.pyplot as plt

# Parameters (https://www.bilenky.com/tandem-specs)
g = 9.81
lb2kg = 0.453592
in2m = 0.0254

m1 = 70                 # Rider 1 mass
m2 = 80                 # Rider 2 mass
b1 = 0.9                # Rider 1 CoM longitudinal position
b2 = 0.3                # Rider 2 CoM longitudinal position
h1 = 0.9                # Rider 1 CoM height
h2 = h1                 # Rider 2 CoM height

me = 10                 # Extra mass
be = -0.1               # Extra mass longitudinal position
he = 29 * in2m          # Extra mass height

mb = 40 * lb2kg         # lb to kg
mt = m1 + m2 + mb + me  # Total mass
w = 68.5 * in2m         # inch to m

Rr = (26 * in2m)/2      # Rear wheel radius
mux = 0.6               # Rear wheel friction coefficient
Rdr = 208.8/1000        # Rear drivetrain radius 
Rdf = 144.2/1000        # Front drivetrain radius 34T (https://www.wolftoothcomponents.com/pages/chainring-diameter-by-tooth-count)
Rc = 175/1000           # Crank length

# System CoM
b = (m1 * b1 + m2 * b2 + me * be)/mt
h = (m1 * h1 + m2 * h2 + me * he)/mt

# Wheelie limit force
Xr = (b * mt * g)/h
Tr = Xr * Rr 

# Grip limit force
Xrg = ((w - b)/(w - mux * h))* mux * mt * g

# Drivetrain
Fc = Tr/Rdr
Fp = (Fc * Rdf)/Rc

print('System CoM: %2.2f %2.2f (b, h) [m] \n' % (b, h))

print('Total mass: %2.2f [kg] \n' % (mt))

print('Minimum Rear Wheel Force for Wheelie: %2.2f [N]' % (Xr))
print('Required Rear wheel torque: %2.2f [Nm] \n' % (Tr))

print('Maximum allowable rear wheel force for grip: %2.2f [N]' % (Xrg))
print('Force difference: %2.2f [N] \n' % (Xrg - Xr))

print('Chain force: {0:2.2f} [N]'.format(Fc))
print('Pedal force (each rider): %2.2f [N] = %2.2f [kg]' % (Fp/2, (Fp/2)/g))

