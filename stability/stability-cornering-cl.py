import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import scipy.linalg as la
from cycler import cycler
import decimal as dc
# from labellines import  labelLines

# plt.rcParams['text.usetex'] = True
plt.rcParams['font.family'] = 'serif'
dc.getcontext().prec = 4

def Damping_ratio(eigenvalue:complex) -> float:
    '''
    Function to calculate the Damping ratio of the given eigenvalue

    Input: Individual complex eigenvalue

    Output: Damping ratio of the given eigenvalue
    
    '''	

    real = np.real(eigenvalue)
    img = np.imag(eigenvalue)
    
    chi = -real/np.sqrt(real**2 + img**2)

    # This could be simplified to
    # chi = -eigenvalue.real/np.sqrt(eigenvalue.real**2 + eigenvalue.imag**2)
    # or even more to
    # chi = list(map(lambda eigval: -eigval.real/np.sqrt(eigval.real**2 + eigval.imag**2), eigenvalues))
    # but Pablo Gutiegez said that is not a good practice to use lambda functions in this case

    return chi



def Stab_criteria(chi:float):

    ''' 
    Function to caracterise the Damping ratio of each eigenvalue
    
    Input: Damping ratio of the eigenvalue

    Output: Print the condition of the given eigenvalue according to its damping factor

    '''

    if chi < 0:
        print('Mode is unstable')
    elif chi == 0:
        print('Mode is oscillating')
    elif chi == 1.0:
        print('Mode is critically damped')
    elif (chi > 0) or (chi < 1.0):
        print('Mode is underdamped')
    elif chi > 1:
        print('Mode is overdamped')




# This function was replaced by map function
# u_modulus = list(map(lambda eigval: np.sqrt(eigval.real**2 + eigval.imag**2), u))
# def eigval_module(eigval):

#     # Function to obtain the modulus of eigenvalues array
#     valmod = np.sqrt(eigval.real**2 + eigval.imag**2)
#     return valmod


def filter_oscillatory(eigenvalues: np.ndarray) -> np.ndarray:

    '''
    Function to delete non-oscillatory eigenvalues
    Only remain eigenvalues with its conjugate
        
    '''

    # Array of modulus of eigenvalues
    mod_eigval = list(map(lambda eigval: np.sqrt(eigval.real**2 + eigval.imag**2), eigenvalues))

    # Find unique elements and their counts
    unique_elements, counts = np.unique(mod_eigval, return_counts=True)
    
    # Find indices of unique elements
    unique_indices = np.where(counts == 1)[0]
    
    # Get the unique elements to be deleted
    unique_elements_to_delete = unique_elements[unique_indices]
    
    # Create a mask to identify elements to keep
    mask = np.isin(mod_eigval, unique_elements_to_delete, invert=True)
    
    # Filter array based on the mask
    filtered_arr = eigenvalues[mask]
    
    return filtered_arr


# def delete_conjugate(eigenvalues):
# Replaced by 
# u_positive = list(filter(lambda eig_val: eig_val.imag > 0, u_filtered))
#     unique_eigenvalues = [eigenvalues[i*2] for i in range(len(eigenvalues)//2)]
#     return unique_eigenvalues


# def module_list(eigenvalues):
# Replaced by
# u_modulus_positive = list(map(lambda eigval: np.sqrt(eigval.real**2 + eigval.imag**2), u_positive))
#     mod = [np.sqrt(eig.real**2 + eig.imag**2) for eig in eigenvalues] 
#     return mod


def max_DoF(eigenvector: np.ndarray):
    '''
    Function to calculate the maximum degree of freedom of the eigenvector
    
    Input: eigenvector
    
    Output: maximum degree of freedom of the eigenvector
    
    '''

    eigvec_t = np.transpose(eigenvector)
    for i in eigvec_t:
        i2 = list(i)
        idx = i2.index(max(i))

        if idx == 0:
            print('V_y')
        elif idx == 1:
            print('psi dot')
        elif idx == 2:
            print('phi dot')
        elif idx == 3:
            print('delta dot')
        elif idx == 4:
            print('beta dot')
        elif idx == 5:
            print('alpha_r')
        elif idx == 6:
            print('alpha_f')
        elif idx == 7:
            print('phi')
        elif idx == 8:
            print('delta')
        elif idx == 9:
            print('beta')

def eig_weave(eigenvalue):
    '''
    Function to determine if the mode is a weave mode
    
    Input: eigenvalue

    Output: 
    
    '''
    weave = []
    for i in eigenvalue:
        if i.imag > 0 and i.imag <= 35 and i.real > -15 and i.real < 5:
            weave.append(i)

    return weave


# Motorcycle constant parameters ----- ----- ----- -----
g = 9.81                    # Gravity
w = 1.448                   # Wheelbase
eps = np.radians(26.8)      # Caster angle
a_n = 0.105                 # Trail
m_0 = 195                   # Motorcycle mass
b_0 = 0.722                 # CoM longitudinal position
h_0 = 0.482                 # CoM vertical position
I_0xx = 13.5                # Moments of inertia
I_0xz = 3                   # Moments of inertia
I_0zz = 55                  # Moments of inertia
m = 270                     # Total mass (w/rider)
b = 0.688                   # CoM longitudinal position (w/rider)
h = 0.64                    # CoM vertical position (w/rider)
I_xx = 35.5                 # Moments of inertia (w/rider)
I_xz = -1.7                 # Moments of inertia (w/rider)
I_zz = 59.3                 # Moments of inertia (w/rider)
m_f = 34                    # Front assembly mass
e_f = 0.025                 # Front CoM coordinates 
h_f = 0.6                   # Front CoM coordinates
I_fzz = 0.83                # Front moment of inertia
I_omega_f = 0.6             # Front wheel spin inertia
I_omega_r = 0.8             # Rear wheel spin inertia
c_delta = 1                 # Steering damping

R_f = 0.294                 #Radio rueda delantera
R_r = 0.299                 #Radio rueda trasera
rho_f = 0.064               #Radio de la cross-section delantera
rho_r = 0.078               #Radio de la cross-section trasera
k_alpha_f = 16              #Rigidez de viraje normalizada
k_alpha_r = 14.5            #Rigidez de viraje normalizada
k_phi_f = 0.85              #Rigidez camber normalizada
k_phi_r = 0.95              #Rigidez camber normalizada
k_a_f = -0.2                #Rigidez auto alineante normalizada
k_a_r = -0.2                #Rigidez auto alineante normalizada
k_t_f = 0.015               #Rigidez de torsión
k_t_r = 0.018               #Rigidez de torsión
k_l_f = 160000              #Rigidez estructural transversal
k_l_r = 140000              #Rigidez estructural transversal

l_beta = 0.67               #Punto de flexión horquilla
l_b = l_beta
k_beta = 38000              #Rigidez de flexión
m_b = 18                    #Masa de flexión (Masa de horquilla?)
e_b = 0                     #CoM horquilla
h_b = 0.35                  #CoM horquilla
I_bxx = 0.8                 #Momento de inercia


#Aerodynamic parameters ----- ----- ----- ----- -----

CdA = 0.467                 #Factor arrastre aerodinámico
h_A = 0.35                  #Altura centro aerodinámico
l_A = 1.16                  #Posición longitudinal centro aerodinámico
chord = 0.1
span = 0.2
Num_wing = 5
Surface = span * chord * Num_wing          #Superficie
# Cl = 1.5                    #Coeficiente de sustentación
ARatio = span/chord           #Aspect ratio
e = 0.8                     #Oswald efficiency number

Cd_0 = 0.0
# Cd = Cd_0 + (Cl**2)/(np.pi*ARatio*e)

#--------------------------------------------------

a_x = 0                     #Aceleración
omega_f_dot = 0             #Aceleración angular rueda
omega_r_dot = 00             #Aceleración angular rueda

N_r_0 = ((w - b)/w) * m * g
N_f_0 = (b/w) * m * g

#Asumido---------------------------------

k_gamma_f = k_phi_f
k_gamma_r = k_phi_r


I_bzz = I_bxx        
x_f    = e_f          
x_b    = e_b              

#---------------------------------------

b_f = w + (x_f + a_n - h_f * np.sin(eps))/np.cos(eps)
b_b = w + (x_b + a_n - h_b * np.sin(eps))/np.cos(eps)
z_b = l_b + ((a_n + x_b) * np.sin(eps) - h_b)/np.cos(eps)

omega_f_dot = 0             #Aceleración angular rueda
omega_r_dot = 0             #Aceleración angular rueda
X_f = 0                     #Fuerza longitudinal rueda delantera
X_f0 = 0
# R_c = 10000                   #Curvature radius

alpha_r0_prime = 0          #Ojo con esto, le puse =0 porque se supone que no hay deriva inicial
alpha_f0_prime = 0          #Esto hace que desaparezca un k_gamma_f en la matriz A

# phi_0 = np.radians(0)                   #Initial roll angle  

# Aero values ----- ----- ----- ----- -----
rho_air = 1.2041
w_A = w   


#--------------------------------------------------------------------

DampingFactor = np.arange(0.1, 0.6, 0.1)
img_df = np.arange(0, 110, 10)
DF_total = []

for ij in DampingFactor:
    real_df = -img_df*ij
    DF_total.append(real_df)

#--------------------------------------------------------------------
V_i = 5
V_f = 101
Vx_rango = np.linspace(V_i,V_f,100)
# Vx_rango = np.arange(V_i,V_f,1)
phi_0 = np.radians(60)

xi = -43
xd = 5
ya = 90

xstab = -39
ystab = 35

xuns = 0.5
yuns = 35


# lift_coef_iter = np.arange(0, 2.1, 0.5)
# lift_coef_iter = [0.5, 1.0, 1.5, 2.0, 3.0]
lift_coef_iter = [0, 0.5, 1.0, 2.0]


real_total = []
img_total = []
weave_total = []

for j in lift_coef_iter:

    Cl = j
    Cd = Cd_0 + (Cl**2)/(np.pi*ARatio*e)
    
    E = np.zeros((10,10))
    E[0,0] = m
    E[0,1] = m*b
    E[0,2] = h*m*np.cos(phi_0)
    E[0,3] = e_f*m_f
    E[0,4] = -m_b*z_b

    E[1,0] = m*b
    E[1,1] = I_zz + b**2*m
    E[1,2] = -I_xz + b*h*m
    E[1,3] = I_fzz*np.cos(eps) + b_f*e_f*m_f
    E[1,4] = -I_bxx*np.sin(eps) - b_b*m_b*z_b

    E[2,0] = m*h
    E[2,1] = -I_xz + b*h*m
    E[2,2] = I_xx + h**2*m
    E[2,3] = I_fzz*np.sin(eps) + e_f*h_f*m_f
    E[2,4] = I_bxx*np.cos(eps) - h_b*m_b*z_b

    E[3,0] = e_f*m_f
    E[3,1] = I_fzz*np.cos(eps) + b_f*e_f*m_f
    E[3,2] = I_fzz*np.sin(eps) + e_f*h_f*m_f
    E[3,3] = I_fzz + e_f**2*m_f
    E[3,4] = - e_b*m_b*z_b

    E[4,0] = -m_b*z_b
    E[4,1] = -I_bxx*np.sin(eps) - b_b*m_b*z_b
    E[4,2] = I_bxx*np.cos(eps) - h_b*m_b*z_b
    E[4,3] = - e_b*m_b*z_b
    E[4,4] = I_bzz + m_b*z_b**2

    E[5,5] = k_alpha_r

    E[6,6] = k_alpha_f

    E[7,7] = 1
    E[8,8] = 1 
    E[9,9] = 1

                
    E2 = np.linalg.inv(E)

    A_total = []
    A_total2 = []
    Normal_f = [N_f_0]
    Normal_r = [N_r_0]
    
    for i in Vx_rango:
        V_x = i
        # Constants ----- ----- ----- ----- -----
        F_ad = 0.5 * rho_air * V_x**2 * (CdA + Cd*Surface)
        DownForce = 0.5 * rho_air * Cl * Surface * V_x**2
        X_r0 = F_ad
        X_r = 0      
        b_A = b

        try :
            R_c = V_x**2/(g*np.tan(phi_0))
        except ZeroDivisionError:
            R_c = 1e6
        
        lateral_acc = V_x**2/(R_c)

        psi_dot_0 = V_x/R_c

        # print('Curvatue radius: ', R_c)
        # print('Lateral acceleration: ', lateral_acc)

        delta_0 = np.arctan((w*np.cos(phi_0))/(R_c * np.cos(eps)))

        # print('delta: ', np.degrees(delta_0))
        # print('\n')

        p_wr1 = V_x/(R_r + rho_r * (np.cos(phi_0) - 1))
        p_wr2 = V_x*rho_r*np.sin(phi_0)/(R_r + rho_r*(np.cos(phi_0) - 1))**2

        p_phif1 = np.arcsin(np.sin(delta_0)*np.sin(eps)*np.cos(phi_0) + np.sin(phi_0)*np.cos(delta_0))
        p_phif2 = (np.cos(eps)*np.cos(phi_0))/np.cos(p_phif1)
        p_phif3 = (-np.sin(delta_0)*np.sin(phi_0) + np.sin(eps)*np.cos(delta_0)*np.cos(phi_0))/np.cos(p_phif1)
        p_phif4 = (-np.sin(delta_0)*np.sin(eps)*np.sin(phi_0) + np.cos(delta_0)*np.cos(phi_0))/np.cos(p_phif1)

        p_Delta1 = (delta_0*np.cos(eps))/(np.cos(phi_0))
        p_Delta2 = np.cos(eps)/np.cos(phi_0)
        p_Delta3 = delta_0*np.sin(phi_0)*np.cos(eps)/np.cos(phi_0)**2
        p_Delta4 = np.sin(eps)/np.cos(phi_0)

        p_wf1 = V_x/(R_f + rho_f*(np.cos(p_phif1) - 1))
        p_wf2 = V_x*rho_f*(np.sin(delta_0)*np.sin(eps)*np.cos(phi_0) + np.sin(phi_0)*np.cos(delta_0))*np.cos(eps)/(R_f + rho_f*(np.cos(p_phif1) - 1))**2
        p_wf3 = V_x*rho_f*(-np.sin(delta_0)*np.sin(phi_0) + np.sin(eps)*np.cos(delta_0)*np.cos(phi_0))*\
            (np.sin(delta_0)*np.sin(eps)*np.cos(phi_0) + np.sin(phi_0)*np.cos(delta_0))/((R_f + rho_f*(np.cos(p_phif1) - 1))**2*np.cos(phi_0))
        p_wf4 = V_x*rho_f*(-np.sin(delta_0)*np.sin(eps)*np.sin(phi_0) + np.cos(delta_0)*np.cos(phi_0))*\
            (np.sin(delta_0)*np.sin(eps)*np.cos(phi_0) + np.sin(phi_0)*np.cos(delta_0))/((R_f + rho_f*(np.cos(p_phif1) - 1))**2*np.cos(phi_0))
            
        p_Nr1 = ((w - b)/w) * m * g + (h_A/w) * F_ad + (1 - b_A/w_A)*DownForce*np.cos(phi_0)
        p_Nr2 = ((b_A/w_A)-1) * DownForce * np.sin(phi_0)

        p_Nf1 = (b/w) * m * g - (h_A/w) * F_ad + (b_A/w_A)*DownForce*np.cos(phi_0)
        p_Nf2 = -(b_A/w_A) * DownForce * np.sin(phi_0)

        p_Yr1 = (k_alpha_r * alpha_r0_prime + k_gamma_r * phi_0) * p_Nr1
        p_Yr2 = k_alpha_r * p_Nr1
        p_Yr3 = k_gamma_r * p_Nr1 + p_Yr1 * p_Nr2

        p_Yf1 = (k_alpha_f * alpha_f0_prime + k_gamma_f * p_phif1) * p_Nf1
        p_Yf2 = k_alpha_f * p_Nf1
        p_Yf3 = k_gamma_f * p_Nf1 * p_phif2
        p_Yf4 = k_gamma_f * p_Nf1 * p_phif3
        p_Yf5 = k_alpha_f * alpha_f0_prime + k_gamma_f*(p_phif1 * p_Nf2 + p_Nf1 * p_phif4)

        p_Mr1 = (k_a_r * alpha_r0_prime + k_t_r * phi_0) * p_Nr1
        p_Mr2 = k_a_r * p_Nr1
        p_Mr3 = k_t_r * p_Nr1 + p_Mr1 * p_Nr2

        p_Mf1 = (k_a_f * alpha_f0_prime + k_t_f * p_phif1) * p_Nf1
        p_Mf2 = k_a_f * p_Nf1
        p_Mf3 = k_t_f * p_Nf1 * p_phif2
        p_Mf4 = k_t_f * p_Nf1 * p_phif3
        p_Mf5 = k_a_f * alpha_f0_prime + k_t_f*(p_phif1 * p_Nf2 + p_Nf1 * p_phif4)

        p_alphar1 = (k_l_r * V_x)/p_Nr1
        p_alphaf1 = (k_l_f * V_x)/p_Nf1


        # Matrix A
        # DO NOT CHANGE THIS UNLESS YOU KNOW EXACTLY WHAT YOU ARE DOING
        A = np.zeros((10,10))

        A[0,1] = -V_x*m
        A[0,5] = p_Yr2
        A[0,6] = p_Yf2
        A[0,7] = -DownForce*np.cos(phi_0) + X_f0*p_Delta1 + p_Yf5 + p_Yr3
        A[0,8] = X_f0*p_Delta2 + p_Yf4
        A[0,9] = -X_f0*p_Delta4 + p_Yf3


        A[1,1] = -V_x*b*m
        A[1,2] = I_omega_f*p_wf1*p_phif4 + I_omega_f*p_wf4*np.sin(p_phif1) + I_omega_r*p_wr1 + I_omega_r*p_wr2*np.sin(phi_0)
        A[1,3] = I_omega_f*p_wf1*p_phif3 + I_omega_f*p_wf3*np.sin(p_phif1)
        A[1,4] = I_omega_f*p_wf1*p_phif2 + I_omega_f*p_wf2*np.sin(p_phif1)
        A[1,5] = p_Mr2
        A[1,6] = p_Mf2 + p_Yf2*w
        A[1,7] = a_x*h*m*np.cos(phi_0) -DownForce*b_A*np.cos(phi_0) + F_ad*h_A*np.cos(phi_0) - X_f0*rho_f*np.cos(phi_0) -\
            X_r0*rho_r*np.cos(phi_0) + p_Mf5 + p_Mr3 + p_Yf5*w
        A[1,8] = a_x*e_f*m_f + X_f0*a_n - X_f0*rho_f*np.sin(eps) + X_f0*w*np.cos(eps) + p_Mf4 + p_Yf4*w
        A[1,9] = - a_x*m_b*z_b + X_f0*l_b - X_f0*rho_f*np.cos(eps) - X_f0*w*np.sin(eps) + p_Mf3 + p_Yf3*w


        A[2,1] = - I_omega_f*p_wf1 - I_omega_r*p_wr1 - V_x*h*m
        A[2,2] = - I_omega_f*p_Delta1*p_wf4 - I_omega_f*p_Delta3*p_wf1
        A[2,3] = - I_omega_f*p_Delta1*p_wf3 - I_omega_f*p_Delta2*p_wf1
        A[2,4] = - I_omega_f*p_Delta1*p_wf2 + I_omega_f*p_Delta4*p_wf1
        A[2,7] = a_n*delta_0*p_Nf2 - delta_0*p_Nf2*rho_f*np.sin(eps) + g*h*m*np.cos(phi_0) - p_Nf1*rho_f*np.cos(phi_0) - \
            p_Nf2*rho_f*np.sin(phi_0) - p_Nr1*rho_r*np.cos(phi_0) - p_Nr2*rho_r*np.sin(phi_0) - (I_omega_f*p_wf4*psi_dot_0 + I_omega_r*p_wr2*psi_dot_0)
        A[2,8] = a_n*p_Nf1 + e_f*g*m_f - p_Nf1*rho_f*np.sin(eps) - I_omega_f*p_wf3*psi_dot_0
        A[2,9] = -g*m_b*z_b + l_b*p_Nf1 - p_Nf1*rho_f*np.cos(eps) - I_omega_f*p_wf2*psi_dot_0


        A[3,1] = - I_omega_f*p_wf1*np.sin(eps) - V_x*e_f*m_f
        A[3,2] = I_omega_f*p_wf1*np.cos(eps)
        A[3,3] = -c_delta
        A[3,4] = I_omega_f*p_wf1
        A[3,6] = -a_n*p_Yf2 + p_Mf2*np.cos(eps)
        A[3,7] = -X_f0*p_phif4*rho_f*np.cos(p_phif1)*np.cos(eps) + a_n*p_Nf1*p_phif4*np.cos(p_phif1) + a_n*p_Nf2*np.sin(p_phif1) - \
            a_n*p_Yf5 + e_f*g*m_f*np.sqrt(-np.sin(delta_0)**2*np.sin(eps)**2*np.cos(phi_0)**2 - 2*np.sin(delta_0)*np.sin(eps)*np.sin(phi_0)*np.cos(delta_0)*np.cos(phi_0) - np.sin(phi_0)**2*np.cos(delta_0)**2 + 1) + \
                p_Mf5*np.cos(eps) - p_Nf1*p_phif4*rho_f*np.sin(eps)*np.cos(p_phif1) - p_Nf2*rho_f*np.sin(p_phif1)*np.sin(eps) - \
                I_omega_f*p_wf4*psi_dot_0
        A[3,8] = -X_f0*p_phif3*rho_f*np.cos(p_phif1)*np.cos(eps) + a_n*p_Nf1*p_phif3*np.cos(p_phif1) - \
            a_n*p_Yf4 + a_x*e_f*m_f*np.cos(eps) + e_f*g*m_f*np.sin(eps) + p_Mf4*np.cos(eps) - \
                p_Nf1*p_phif3*rho_f*np.sin(eps)*np.cos(p_phif1) - (I_omega_f*p_wf3*psi_dot_0 + a_x*e_f*m_f*np.cos(eps))
        A[3,9] = X_f0*a_n*np.sin(eps) + X_f0*l_b*np.cos(eps) - X_f0*p_phif2*rho_f*np.cos(p_phif1)*np.cos(eps) + \
            a_n*p_Nf1*p_phif2*np.cos(p_phif1) - a_n*p_Nf1*np.cos(eps) - a_n*p_Yf3 - a_x*m_b*z_b*np.cos(eps) - \
                g*m_b*z_b*np.sin(eps) + l_b*p_Nf1*np.sin(eps) + p_Mf3*np.cos(eps) - p_Nf1*p_phif2*rho_f*np.sin(eps)*np.cos(p_phif1) - \
                I_omega_f*p_wf2*psi_dot_0

        A[4,1] = -I_omega_f*p_wf1*np.cos(eps) + V_x*m_b*z_b
        A[4,2] = -I_omega_f*p_wf1*p_phif4
        A[4,3] = -I_omega_f*p_wf1*p_phif3
        A[4,4] = -I_omega_f*p_wf1*p_phif2
        A[4,6] = -l_b*p_Yf2*np.cos(p_phif1) - p_Mf2*np.sin(eps)
        A[4,7] = X_f0*p_phif4*rho_f*np.sin(eps)*np.cos(eps) - g*m_b*p_phif4*z_b*np.cos(p_phif1) + \
            l_b*p_Nf1*p_Yf1*p_phif4*np.sin(p_phif1) + l_b*p_Nf1*p_phif4*np.cos(p_phif1) + l_b*p_Nf2*np.sin(p_phif1) - \
                l_b*p_Yf5*np.cos(p_phif1) - p_Mf5*np.sin(eps) - p_Nf1*p_phif4*rho_f*np.cos(p_phif1)*np.cos(eps) - \
                    p_Nf2*rho_f*np.sin(p_phif1)*np.cos(eps) - I_omega_f*p_wf4*psi_dot_0
        A[4,8] = X_f0*p_phif3*rho_f*np.sin(eps)*np.cos(eps) - a_x*m_b*z_b*np.cos(eps) - g*m_b*p_phif3*z_b*np.cos(p_phif1) + \
            l_b*p_Nf1*p_Yf1*p_phif3*np.sin(p_phif1) + l_b*p_Nf1*p_phif3*np.cos(p_phif1) - l_b*p_Yf4*np.cos(p_phif1) - \
                p_Mf4*np.sin(eps) - p_Nf1*p_phif3*rho_f*np.cos(p_phif1)*np.cos(eps) - I_omega_f*p_wf3*psi_dot_0
        A[4,9] = X_f0*p_phif2*rho_f*np.sin(eps)*np.cos(eps) + a_x*m_b*z_b*np.sin(eps) - g*m_b*p_phif2*z_b*np.cos(p_phif1) - \
            k_beta + l_b*p_Nf1*p_Yf1*p_phif2*np.sin(p_phif1) + l_b*p_Nf1*p_phif2*np.cos(p_phif1) - l_b*p_Yf3*np.cos(p_phif1) - \
                p_Mf3*np.sin(eps) - p_Nf1*p_phif2*rho_f*np.cos(p_phif1)*np.cos(eps) - I_omega_f*p_wf2*psi_dot_0

        A[5,0] = - k_l_r/p_Nr1
        A[5,2] = 1 - k_gamma_r
        A[5,5] = - p_alphar1

        A[6,0] = -p_alphaf1/V_x
        A[6,1] = -p_alphaf1*w/V_x
        A[6,2] = -k_gamma_f*p_phif4 + p_phif4 
        A[6,3] = -k_gamma_f*p_phif3 + p_phif3 + a_n*p_alphaf1/V_x
        A[6,4] = -k_gamma_f*p_phif2 + p_phif2 + l_b*p_alphaf1/V_x - p_alphaf1*rho_f*np.cos(eps)/V_x
        A[6,6] = -p_alphaf1
        A[6,7] = delta_0*p_alphaf1*np.sin(phi_0)*np.cos(eps)/np.cos(phi_0)**2
        A[6,8] = p_alphaf1*np.cos(eps)/np.cos(phi_0)
        A[6,9] = -p_alphaf1*np.sin(eps)/np.cos(phi_0)

        A[7,2] = 1
        A[8,3] = 1
        A[9,4] = 1

        wobble = []
        # weave = []

        A_total.append(A)
        A_total2.append(E2@A)

    real_temporary = []
    img_temporary = []
    weave = []


    for k in A_total:
        u, v  = np.linalg.eig(np.dot(E2, k))

        u_filtered = filter_oscillatory(u)

        # Function to delete the conjugate of imaginary eigenvalues, only remain the positive part
        u_positive = list(filter(lambda eig_val: eig_val.imag > 0, u_filtered))

        # This is to delete the maximum value that is not relevant for the present work
        u_positive.remove(u_positive[0])

        # Function to obtain the modulus of eigenvalues array
        u_modulus = list(map(lambda eigval: np.sqrt(eigval.real**2 + eigval.imag**2), u))

        u_modulus_filtered = list(map(lambda eigval: np.sqrt(eigval.real**2 + eigval.imag**2), u_filtered))
        
        u_modulus_positive = list(map(lambda eigval: np.sqrt(eigval.real**2 + eigval.imag**2), u_positive))

        v_modulus = list(map(lambda eigval: np.sqrt(eigval.real**2 + eigval.imag**2), v))

        real_temporary.append(np.real(u_positive))
        img_temporary.append(np.imag(u_positive))

        com1 = eig_weave(u_filtered)
        if len(com1) > 0:
            weave.append(com1)
    
    real_total.append(real_temporary)
    img_total.append(img_temporary)
    weave_total.append(weave)
    

fig, ax = plt.subplots()

for ii in range(len(real_total)):
    if ii == 0:
        symbol = '1'
        colorit = 'black'
        fcolorit = colorit
    elif ii == 1:
        symbol = 'o'
        colorit = 'blue'
        fcolorit = 'none'
    elif ii == 2:
        symbol = '^'
        colorit = 'red'
        fcolorit = 'none'
    elif ii == 3:
        symbol = 's'
        colorit = 'green'
        fcolorit = 'none'
    elif ii == 4:
        symbol = 'D'
        colorit = 'orange'
        fcolorit = 'none'
    elif ii == 5:
        symbol = 'X'
        colorit = 'cyan'
        fcolorit = 'none'
    elif ii == 6:
        symbol = 'P'
        colorit = 'purple'
        fcolorit = 'none'
    elif ii ==7:
        symbol = 'h'
        colorit = 'yellow'
        fcolorit = 'none'

    sizecounter = 0
    for jj in range(len(real_total[ii])):
        ax.scatter(real_total[ii][jj], img_total[ii][jj], marker=symbol, \
                facecolors=fcolorit, edgecolors=colorit, s=10+sizecounter, label = f'Cl = {lift_coef_iter[ii]}')
        sizecounter += 1

black_tri = mlines.Line2D([], [], color = 'black', marker = '1', \
                           linestyle = 'None', markersize = 10, label = r'$C_l = 0$')
blue_circle = mlines.Line2D([], [], color = 'blue', marker = 'o', \
                            linestyle = 'None', markersize = 10, fillstyle = 'none', label = r'$C_l = 0.5$')
red_triangle = mlines.Line2D([], [], color = 'red', marker = '^', \
                            linestyle = 'None', markersize = 10, fillstyle = 'none', label = r'$C_l = 1.0$')
green_square = mlines.Line2D([], [], color = 'green', marker = 's', \
                            linestyle = 'None', markersize = 10, fillstyle = 'none', label = r'$C_l = 2.0$')
orange_diamond = mlines.Line2D([], [], color = 'orange', marker = 'D', \
                            linestyle = 'None', markersize = 10, fillstyle = 'none', label = r'$C_l = 3.0$')

ax.legend(handles = [black_tri, blue_circle, red_triangle, green_square], loc = 'lower left', fontsize = 15)
ax.axvline(x = 0, color = 'k', linestyle = '-')
ax.set_xlabel('Real part [1/s]',size=15)
ax.set_ylabel('Imaginary part [1/s]', size=15)
ax.set_xlim([xi, xd])
ax.set_ylim([-1, ya])
ax.fill_betweenx(np.arange(-5, 105), 0, 30, where=(np.arange(-5, 105) >= -5), color='lightgray', alpha=0.5)


# ax.text(xstab, ystab, r'\textbf{Stable}', size=15)
# ax.text(xuns, yuns, r'\textbf{Unstable}', size=15, rotation = 'vertical')
# ax.text(-13, 75, r'\textit{Wobble}', size=15)
# ax.text(-11, 5, r'\textit{Weave}', size=15)
# ax.text(-27, 27, r'\textit{Rear Wobble}', size=15)

ax.plot(DF_total[0], img_df, color = 'grey', linestyle = '--', linewidth = 1, label = r'$\zeta = 0.1$')
ax.plot(DF_total[1], img_df, color = 'grey', linestyle = '--', linewidth = 1, label = r'$\zeta = 0.2$')
ax.plot(DF_total[2], img_df, color = 'grey', linestyle = '--', linewidth = 1, label = r'$\zeta = 0.3$')
ax.plot(DF_total[3], img_df, color = 'grey', linestyle = '--', linewidth = 1, label = r'$\zeta = 0.4$')
ax.plot(DF_total[4], img_df, color = 'grey', linestyle = '--', linewidth = 1, label = r'$\zeta = 0.5$')

# labelLines(ax.get_lines(), zorder = 5, color = 'k', fontsize = 15, xvals = (-1, -15))


plt.tick_params(labelsize=15)
plt.grid()
plt.show()



vx0 = np.linspace(V_i, V_f, len(weave_total[0]))
vx1 = np.linspace(V_i, V_f, len(weave_total[1]))
vx2 = np.linspace(V_i, V_f, len(weave_total[2]))
vx3 = np.linspace(V_i, V_f, len(weave_total[3]))

x_shadow = np.linspace(0, 105, 100)
y_shadow = np.linspace(5, 5, 100)

plt.plot(vx0, weave_total[0], 'k', label = r'$C_l = 0$')
plt.plot(vx1, weave_total[1], 'b', label = r'$C_l = 0.5$')
plt.plot(vx2, weave_total[2], 'r', label = r'$C_l = 1$')
plt.plot(vx3, weave_total[3], 'g', label = r'$C_l = 2$')

# legend_weave = plt.legend(handles=[plt.Line2D([0], [0], color='r', linestyle='-'),
#                                    plt.Line2D([0], [0], color='b', linestyle='-'),
#                                    plt.Line2D([0], [0], color='g', linestyle='-')],
#                            labels=['Lift coef = 0', 'Lift coef = 0.75', 'Lift coef = 1.5'],
#                            loc='upper right', fontsize = 15)

plt.xlabel('Longitudinal speed [m/s]', fontsize=18)
plt.ylabel('Real part [1/s]', fontsize=18)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.fill_between(x_shadow, y_shadow, color='lightgray', alpha = 0.5)

# plt.text(5, -0.5, r'\textbf{Stable}', size=15)
# plt.text(5, 0.5, r'\textbf{Unstable}', size=15)
plt.hlines(0, 0, 105, colors='k', linestyles='solid')
plt.legend(loc = 'lower right', fontsize = '15')
plt.xlim([0, 105])
plt.ylim([-7.5, 1])
plt.grid()
plt.show()
