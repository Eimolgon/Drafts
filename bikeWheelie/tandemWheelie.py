import numpy as np
import matplotlib.pyplot as plt

def plotBike():
    # Wheels
    rearWheel = plt.Circle((0, Rr), Rr, color='k', fill=False)
    frontWheel = plt.Circle((w, Rf), Rf, color='k', fill=False)

    # CoM
    CoM = plt.Circle((b,h), 0.05, color='r')
    CoM_bike = plt.Circle((bb,hb), 0.025, color='y')
    CoM_rider_1 = plt.Circle((b1,h1), 0.025, color='b')
    CoM_rider_2 = plt.Circle((b2,h2), 0.025, color='b')
    CoM_counterMass = plt.Circle((be,he), 0.025, color='g')

    # Frame
    rear_frame_x, rear_frame_y = [0, w-0.5], [Rr, 1]
    front_frame_x, front_frame_y = [w, w-0.5], [Rf, 1]

    seat_angle = np.deg2rad(70)
    tube_1_x = [1.1, 1.1 - 0.5*np.cos(seat_angle)]
    tube_1_y = [0.3, 0.3 + 0.5*np.sin(seat_angle)]
    tube_2_x = [0.49, 0.49 - 0.5*np.cos(seat_angle)]
    tube_2_y = tube_1_y

    fig, ax = plt.subplots()
    fig.set_figwidth(16)
    fig.set_figheight(8)

    ax.add_patch(rearWheel)
    ax.add_patch(frontWheel)
    ax.add_patch(CoM)
    ax.add_patch(CoM_bike)
    ax.add_patch(CoM_rider_1)
    ax.add_patch(CoM_rider_2)
    ax.add_patch(CoM_counterMass)
    ax.plot(rear_frame_x, rear_frame_y, color='y')
    ax.plot(front_frame_x, front_frame_y, color='r')
    ax.plot(tube_1_x, tube_1_y, color='k')
    ax.plot(tube_2_x, tube_2_y, color='b')

    plt.xlim(-1, 3)
    plt.ylim(0, 2)
    plt.grid()
    plt.show()
    return


# Parameters (https://www.bilenky.com/tandem-specs)
g = 9.81
lb2kg = 0.453592
in2m = 0.0254

m1 = 72                 # Rider 1 mass
m2 = 72                 # Rider 2 mass
b1 = 0.8                # Rider 1 CoM longitudinal position / 1  original green tandem
b2 = 0.2                # Rider 2 CoM longitudinal position / 0.4 original green tandem
h1 = 0.8                # Rider 1 CoM height / 0.9 original
h2 = 0.8                # Rider 2 CoM height

me = 30                 # Extra mass / 0 original
be = -0.2               # Extra mass longitudinal position
he = 0.9                # Extra mass height / 29 inch original

w = 1.9                 # Wheelbase
mfront = 12             
mrear = 17
mb = mfront + mrear     # Bicycle mass
bb = (mfront*w)/mb      # Longitudinal CoM bike w/o riders
hb = 0.5                # Completely random, needs to be checked
mt = m1 + m2 + mb + me  # Total mass


Rr = 0.25               # Rear wheel radius
Rf = 0.34               # Front wheel radius
mux = 0.8               # Rear wheel friction coefficient
Rdr = 208.8/1000        # Rear drivetrain radius 
Rdf = 144.2/1000        # Front drivetrain radius 34T (https://www.wolftoothcomponents.com/pages/chainring-diameter-by-tooth-count)
Rc = 175/1000           # Crank length

# System CoM
b = (m1 * b1 + m2 * b2 + me * be + mb * bb)/mt
h = (m1 * h1 + m2 * h2 + me * he + mb * hb)/mt

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

plotBike()
