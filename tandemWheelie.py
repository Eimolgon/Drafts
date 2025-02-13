import numpy as np
import matplotlib.pyplot as plt

# Parameters (https://www.bilenky.com/tandem-specs)
g = 9.81
lb2kg = 0.453592
in2m = 0.0254

m1 = 72                 # Rider 1 mass
m2 = 72                 # Rider 2 mass
b1 = 1                  # Rider 1 CoM longitudinal position / 0.9 original
b2 = 0.4                # Rider 2 CoM longitudinal position / 0.3 original
h1 = 0.8                # Rider 1 CoM height / 0.9 original
h2 = 0.8                # Rider 2 CoM height

me = 30                 # Extra mass / 0 original
be = -0.2               # Extra mass longitudinal position
he = 0.9                # Extra mass height / 29 inch original

mb = 12 + 17            # Bicycle mass
mt = m1 + m2 + mb + me  # Total mass
w = 1.9                 # Wheelbase

Rr = 0.34               # Rear wheel radius
mux = 0.8               # Rear wheel friction coefficient
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

# Balance angle

alpha = (np.arctan(h/b))*180/np.pi

print('System CoM: %2.2f %2.2f (b, h) [m] \n' % (b, h))

print('Total mass: %2.2f [kg] \n' % (mt))

print('Minimum Rear Wheel Force for Wheelie: %2.2f [N]' % (Xr))
print('Required Rear wheel torque: %2.2f [Nm] \n' % (Tr))

print('Maximum allowable rear wheel force for grip: %2.2f [N]' % (Xrg))
print('Force difference: %2.2f [N] \n' % (Xrg - Xr))

print('Chain force: {0:2.2f} [N]'.format(Fc))
print('Pedal force (each rider): %2.2f [N] = %2.2f [kg] \n' % (Fp/2, (Fp/2)/g))

print('Pitch angle for balance: %2.2f °' % (90 - alpha))

