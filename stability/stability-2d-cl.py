import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eigvals
from cycler import cycler
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# plt.rcParams['text.usetex'] = True
plt.rcParams['font.family'] = 'serif'

def eigen_stab(eigenvalue):
    real = np.real(eigenvalue)
    img = np.imag(eigenvalue)
    
    chi = -real/np.sqrt(real**2 + img**2)

    return chi


def Stab_criteria(chi):
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

def filter_positive_imaginary_part(eigenvalues):
    # filtered_eigenvalues = [ev for ev in eigenvalues if ev.imag > 0 and ev.imag <= 70]
    filtered_eigenvalues = [eig_val for eig_val in eigenvalues if eig_val.imag > 0 and eig_val.imag <= 70 and eig_val.real >= -15]
    return filtered_eigenvalues


g = 9.81                    #Gravedad
w = 1.448                   #Wheelbase
varepsilon = 26.8 * np.pi/180   #Caster angle
a_n = 0.105                 #Trail
m_0 = 195                   #Masa moto
b_0 = 0.722                 #Posición CoM
h_0 = 0.482                 #Posición CoM
I_0xx = 13.5                #Momentos inercia
I_0xz = 3                   #Momentos inercia
I_0zz = 55                  #Momentos inercia
m = 270                     #Masa total (c/ piloto)
b = 0.688                   #CoM pos (c/ piloto)
h = 0.64                    #CoM pos (c/ piloto)
I_xx = 35.5                 #Momentos inercia (c/ piloto)
I_xz = -1.7                 #Momentos inercia (c/ piloto)
I_zz = 59.3                 #Momentos inercia (c/ piloto)
m_f = 34                    #Masa eje delantero
e_f = 0.025                 #CoM delantero 
h_f = 0.6                   #CoM delantero
I_fzz = 0.83                #Momento incercia frontal
I_omega_f = 0.6             #Inercia rueda delantera (giro)
I_omega_r = 0.8             #Inercia rueda trasera (giro)
c_delta = 1                 #Amortiguador direccion

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
l_b = 0.67 ## podria ser    #BUSCAR
k_beta = 38000              #Rigidez de flexión
m_b = 18                    #Masa de flexión (Masa de horquilla?)
e_b = 0                     #CoM horquilla
h_b = 0.35                  #CoM horquilla
I_bxx = 0.8                 #Momento de inercia


cop_pos = [-0.6, 0, 0.6]
lift_coef = [0, -0.75, -1.5]
# Vx_rango = np.linspace(5,101,75)
Vx_rango = np.arange(5, 101, 1)

ss_wob = []                #Speed stability wobble
ss_wea = []                #Speed stability weave
when_stable2 = []
damp_weave = []
damp_wobble = []

DampingFactor = np.arange(0.1, 0.6, 0.1)
img_df = np.arange(0, 110, 10)
DF_total = []

for jj in lift_coef:

    
    #Aero values---------------------------------------

    CdA = 0.467                 #Factor arrastre aerodinámico
    h_A = 0.35                  #Altura centro aerodinámico
    l_A = b #- 0.6               #Posición longitudinal centro aerodinámico [-0.6 -> Rear; 0 centre; +0.6 Front]
    width = 0.1
    length = 0.2
    Num_wing = 4
    S = length * width * Num_wing          #Superficie
    Cl = jj                    #Coeficiente de sustentación
    AR = length/width           #Aspect ratio
    e = 0.8                     #Oswald efficiency number

    Cd_0 = 0.0
    Cd = Cd_0 + (Cl**2)/(np.pi*AR*e)

    #--------------------------------------------------

    a_x = 0                     #Aceleración
    omega_f_dot = 0             #Aceleración angular rueda
    omega_r_dot = 0             #Aceleración angular rueda

    N_r_0 = ((w - b)/w) * m * g
    N_f_0 = (b/w) * m * g

    #Asumido---------------------------------

    k_gamma_f = 1
    k_gamma_r = 1

    k_y_f = k_l_f
    k_y_r = k_l_r


    I_bzz = I_bxx        
    x_f    = e_f          
    x_b    = e_b   

    #---------------------------------------

    b_f = w + (x_f + a_n - h_f * np.sin(varepsilon))/np.cos(varepsilon)
    b_b = w + (x_b + a_n - h_b * np.sin(varepsilon))/np.cos(varepsilon)
    z_b = l_b + ((a_n + x_b) * np.sin(varepsilon) - h_b)/np.cos(varepsilon)


    #--------------------------------------------------------------------
    E = np.zeros((10,10))
    E[0,0] = m
    E[0,1] = m*b
    E[0,2] = m*h
    E[0,3] = m_f * e_f
    E[0,4] = -m_b*z_b

    E[1,1] = m*b**2 + I_zz
    E[1,2] = m*b*h - I_xz
    E[1,3] = m_f*e_f*b_f + I_fzz * np.cos(varepsilon)
    E[1,4] = -m_b*z_b*b_b -I_bxx * np.sin(varepsilon)

    E[2,2] = m*h**2 + I_xx
    E[2,3] = m_f*e_f*h_f + I_fzz * np.sin(varepsilon)
    E[2,4] = -m_b*h_b*z_b + I_bxx * np.cos(varepsilon)

    E[3,3] = m_f*e_f**2 + I_fzz
    E[3,4] = -m_b*e_b*z_b

    E[4,4] = m_b*z_b**2 + I_bzz

    E[5,5] = k_alpha_r

    E[6,6] = k_alpha_f

    E[7,7] = 1
    E[8,8] = 1
    E[9,9] = 1

    for i in range(1, 10):
        for j in range(i):
            E[i, j] = E[j, i]
            
    E2 = np.linalg.inv(E)

    A_total = []
    A_total2 = []
    Lift = []
    Drag = []
    Normal_f = [N_f_0]
    Normal_r = [N_r_0]


    for i in Vx_rango:
        V_x = i
        X_f = 0
        omega_f = V_x/R_f
        omega_r = V_x/R_r

        rho_air = 1.2041
        F_ad = 0.5 * rho_air * V_x**2 * (CdA + Cd*S)
        F_al = 0.5 * rho_air * Cl * S * V_x**2
        X_r = F_ad

        N_r = N_r_0 + (h_A/w) * F_ad - (1 - (l_A/w)) * F_al
        N_f = N_f_0 - (h_A/w) * F_ad - (l_A/w) * F_al


        A = np.zeros((10,10))
        A[0,1] = -m * V_x
        A[0,5] = k_alpha_r * N_r
        A[0,6] = k_alpha_f * N_f
        A[0,7] = k_gamma_f * N_f + k_gamma_r * N_r
        A[0,8] = X_f * np.cos(varepsilon) + N_f * k_gamma_f * np.sin(varepsilon)
        A[0,9] = -X_f * np.sin(varepsilon) + N_f * k_gamma_f * np.cos(varepsilon)

        A[1,1] = -m * b * V_x
        A[1,2] = I_omega_r * omega_r + I_omega_f * omega_f
        A[1,3] = I_omega_f * omega_f * np.sin(varepsilon)
        A[1,4] = I_omega_f * omega_f * np.cos(varepsilon)
        A[1,5] = k_a_r * N_r
        A[1,6] = k_alpha_f * w * N_f + k_a_f * N_f
        A[1,7] = k_t_r * N_r + (k_t_f + w * k_gamma_f) * N_f + h * m * a_x + h_A * F_ad + I_omega_r * omega_r_dot + I_omega_f * omega_f_dot - X_f * rho_f - X_r * rho_r + l_A * F_al
        A[1,8] = k_t_f * N_f * np.sin(varepsilon) + (w * np.cos(varepsilon) - rho_f * np.sin(varepsilon) + a_n) * X_f + m_f * e_f * a_x + I_omega_f * omega_f_dot * np.sin(varepsilon) + N_f * k_gamma_f * w * np.sin(varepsilon)
        A[1,9] = (l_b - rho_f * np.cos(varepsilon) - w * np.sin(varepsilon)) * X_f + I_omega_f * omega_f_dot * np.cos(varepsilon) - m_b * z_b * a_x + k_t_f * N_f * np.cos(varepsilon) + N_f * k_gamma_f * w * np.cos(varepsilon)

        A[2,1] = -m * h * V_x - I_omega_r * omega_r - I_omega_f * omega_f
        A[2,3] = -I_omega_f * omega_f * np.cos(varepsilon)
        A[2,4] = I_omega_f * omega_f * np.sin(varepsilon)
        A[2,7] = m * g * h - rho_f * N_f - rho_r * N_r
        A[2,8] = (a_n - rho_f * np.sin(varepsilon)) * N_f + m_f * e_f * g - I_omega_f * omega_f_dot * np.cos(varepsilon)
        A[2,9] = (l_b - rho_f * np.cos(varepsilon)) * N_f - m_b * z_b * g + I_omega_f * omega_f_dot * np.sin(varepsilon)

        A[3,1] = -m_f * e_f * V_x - I_omega_f * omega_f * np.sin(varepsilon)
        A[3,2] = I_omega_f * omega_f * np.cos(varepsilon)
        A[3,3] = -c_delta
        A[3,4] = I_omega_f * omega_f
        A[3,6] = (k_a_f  * np.cos(varepsilon) - a_n * k_alpha_f) * N_f
        A[3,7] = (a_n * (1 - k_gamma_f) - rho_f * np.sin(varepsilon)) * N_f - rho_f * X_f * np.cos(varepsilon) + m_f * e_f * g + N_f * k_t_f * np.cos(varepsilon)
        A[3,8] = k_gamma_f * a_n * N_f * np.sin(varepsilon)  + A[3,7] * np.sin(varepsilon) - N_f * a_n * k_gamma_f * np.sin(varepsilon)
        A[3,9] = (k_t_f * np.cos(varepsilon)**2 - rho_f * np.sin(varepsilon) * np.cos(varepsilon) + l_b * np.sin(varepsilon)) * N_f - m_b * z_b * (g * np.sin(varepsilon) + a_x * np.cos(varepsilon)) + (a_n * np.sin(varepsilon) - rho_f * np.cos(varepsilon)**2 + l_b * np.cos(varepsilon)) * X_f + I_omega_f * omega_f_dot  - N_f * a_n * k_gamma_f * np.cos(varepsilon)

        A[4,1] = m_b * z_b * V_x - I_omega_f * omega_f *np.cos(varepsilon)
        A[4,2] = -I_omega_f * omega_f
        A[4,3] = -I_omega_f * omega_f * np.sin(varepsilon)
        A[4,4] = -I_omega_f * omega_f * np.cos(varepsilon)
        A[4,6] = -(k_a_f * np.sin(varepsilon) + l_b * k_alpha_f) * N_f
        A[4,7] = ((1 - k_gamma_f) * l_b - k_t_f * np.sin(varepsilon) - rho_f * np.cos(varepsilon)) * N_f + rho_f * X_f * np.sin(varepsilon) - m_b * z_b * g
        A[4,8] =  - m_b * z_b * a_x * np.cos(varepsilon) + A[4,7] * np.sin(varepsilon)
        A[4,9] =  m_b * z_b * a_x * np.sin(varepsilon) + A[4,7] * np.cos(varepsilon) - k_beta

        A[5,0] = -k_y_r / N_r
        A[5,2] = 1 - k_gamma_r
        A[5,5] = -V_x * k_y_r / N_r

        A[6,0] = -k_y_f/N_f
        A[6,1] = (- k_y_f) / N_f * w
        A[6,2] = 1 - k_gamma_f
        A[6,3] = (1 - k_gamma_f) * np.sin(varepsilon) + a_n * k_y_f/N_f
        A[6,4] = (1 - k_gamma_f) * np.cos(varepsilon) + (l_b - rho_f * np.cos(varepsilon))* k_l_f/N_f
        A[6,6] = -(V_x * k_y_f) / N_f
        A[6,8] = V_x*np.cos(varepsilon) * k_y_f/N_f
        A[6,9] = - V_x*np.sin(varepsilon) * k_y_f/N_f

        A[7,2] = 1
        A[8,3] = 1
        A[9,4] = 1

        A_total.append(A)
        Lift.append(F_al)
        Drag.append(F_ad)
        Normal_f.append(N_f)
        Normal_r.append(N_r)


    wobble = []
    weave = []
    chi_weave = []
    chi_wobble = []
    for k in A_total:
        u = np.linalg.eigvals(np.dot(E2, k))
        u2 = filter_positive_imaginary_part(u)
        wobble.append(u2[0])
        weave.append(u2[1])
        chi_wobble.append(eigen_stab(u2[0]))
        chi_weave.append(eigen_stab(u2[1]))



    real_wob = []
    real_wea = []

    for jj in range(len(wobble)):
        real_wob.append(wobble[jj].real)
        real_wea.append(weave[jj].real)

    ss_wob.append(real_wob)
    ss_wea.append(real_wea)
    damp_weave.append(chi_weave)
    damp_wobble.append(chi_wobble)


for ij in DampingFactor:
    real_df = -img_df*ij
    DF_total.append(real_df)


# ----- Weave plot -----

x_shadow = np.linspace(0, 105, 100)
y_shadow = np.linspace(5, 5, 100)

fig, ax = plt.subplots()

ax.plot(Vx_rango[1:len(Vx_rango)-1], ss_wea[0][1:len(Vx_rango)-1], color = 'k', linestyle = 'solid', label = 'Lift coef = 0')
ax.plot(Vx_rango[1:len(Vx_rango)-1], ss_wea[1][1:len(Vx_rango)-1], color = 'k', linestyle = 'dashed', label = 'Lift coef = 0.75')
ax.plot(Vx_rango[1:len(Vx_rango)-1], ss_wea[2][1:len(Vx_rango)-1], color = 'k', linestyle = 'dashdot', label = 'Lift coef = 1.5')

# plt.text(30, -1.5, 'Weave', size=16, fontstyle='italic')


# Create the first legend for wobble linek
legend_weave = plt.legend(handles=[plt.Line2D([0], [0], color='k', linestyle='solid'),
                                   plt.Line2D([0], [0], color='k', linestyle='dashed'),
                                   plt.Line2D([0], [0], color='k', linestyle='dashdot')],
                           labels=['Lift coef = 0', 'Lift coef = 0.75', 'Lift coef = 1.5'],
                           loc='lower left', fontsize = 15)

# plt.title('Weave stability with CoP aligned with CoM')
plt.xlabel('Longitudinal speed [m/s]', fontsize=18)
plt.ylabel('Real part [1/s]', fontsize=18)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.fill_between(x_shadow, y_shadow, color='lightgray', alpha = 0.5)
plt.hlines(0, 0, 105, colors='k', linestyles='solid')
# plt.text(40, 0.5, 'Unstable', size=18, fontweight='bold')
# plt.text(10, -2.5, 'Stable', size=18, fontweight='bold')
plt.xlim(0, 105)
plt.ylim(-5.5, 1.5)
# plt.grid()

xx1, xx2, yy1, yy2 = 76, 97, -0.25, 0.25
axins = ax.inset_axes([0.35, 0.4, 0.35, 0.2],
    xlim=(xx1, xx2), ylim=(yy1, yy2))

axins.plot(Vx_rango, ss_wea[0], color = 'k', linestyle = 'solid', label = 'Lift coef = 0')
axins.plot(Vx_rango, ss_wea[1], color = 'k', linestyle = 'dashed', label = 'Lift coef = 0.75')
axins.plot(Vx_rango, ss_wea[2], color = 'k', linestyle = 'dashdot', label = 'Lift coef = 1.5')
axins.fill_between(x_shadow, y_shadow, color='lightgray', alpha = 0.5)
axins.hlines(0, 0, 105, colors='k', linestyles='solid')
axins.grid()
ax.indicate_inset_zoom(axins, edgecolor="black")

# plt.show()



# ----- Wobble plot -----

plt.plot(Vx_rango[1:len(Vx_rango)-1], ss_wob[0][1:len(Vx_rango)-1], color = 'k', linestyle = 'solid', label = 'Lift coef = 0')
plt.plot(Vx_rango[1:len(Vx_rango)-1], ss_wob[1][1:len(Vx_rango)-1], color = 'k', linestyle = 'dashed', label = 'Lift coef = 0.75')
plt.plot(Vx_rango[1:len(Vx_rango)-1], ss_wob[2][1:len(Vx_rango)-1], color = 'k', linestyle = 'dashdot', label = 'Lift coef = 1.5')
plt.plot(DF_total[0], img_df, 'k--', label = 'Damping factor = 0.1')
plt.text(42, -7.8, r'\textit{wobble}', size=15)
plt.text(82, -1, r'\textit{weave}', size=15)

legend_wobble = plt.legend(handles=[plt.Line2D([0], [0], color='k', linestyle='solid'),
                                   plt.Line2D([0], [0], color='k', linestyle='dashed'),
                                   plt.Line2D([0], [0], color='k', linestyle='dashdot')],
                           labels=['Lift coef = 0', 'Lift coef = 0.75', 'Lift coef = 1.5'],
                           loc='lower left', fontsize = 15)

plt.xlabel('Longitudinal speed [m/s]', fontsize=18)
plt.ylabel('Real part [1/s]', fontsize=18)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.fill_between(x_shadow, y_shadow, color='lightgray', alpha = 0.5)
plt.hlines(0, 0, 105, colors='k', linestyles='solid')
plt.text(10, 0.5, r'\textbf{Unstable}', size=18, fontweight='bold')
plt.text(10, -6.5, r'\textbf{Stable}', size=18, fontweight='bold')
plt.xlim(0, 105)
plt.ylim(-10.5, 2)
plt.grid()
plt.show()


# ----- Damping factor weave -----

exit()
fig_dfwe, ax_dfwe = plt.subplots()

ax_dfwe.plot(Vx_rango[1:len(Vx_rango)-1], damp_weave[0][1:len(Vx_rango)-1], linestyle = 'solid', label = 'Lift coef = 0')
ax_dfwe.plot(Vx_rango[1:len(Vx_rango)-1], damp_weave[1][1:len(Vx_rango)-1], linestyle = 'dashed', label = 'Lift coef = 0.75')
ax_dfwe.plot(Vx_rango[1:len(Vx_rango)-1], damp_weave[2][1:len(Vx_rango)-1], linestyle = 'dashdot', label = 'Lift coef = 1.5')


# Create the first legend for wobble lines
legend_weave = plt.legend(handles=[plt.Line2D([0], [0], color='r', linestyle='-'),
                                   plt.Line2D([0], [0], color='b', linestyle='-'),
                                   plt.Line2D([0], [0], color='g', linestyle='-')],
                           labels=['Lift coef = 0', 'Lift coef = 0.75', 'Lift coef = 1.5'],
                           loc='lower left', fontsize = 15)

plt.xlabel('Longitudinal speed [m/s]', fontsize=18)
plt.ylabel('Damping factor', fontsize=18)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

plt.hlines(0, 0, 105, colors='k', linestyles='solid')

plt.xlim(0, 105)
plt.ylim(-0.15, 0.6)
plt.grid()

xx1_dfwe, xx2_dfwe, yy1_dfwe, yy2_dfwe = 76, 98, -0.05, 0.05
axins_dfwe = ax_dfwe.inset_axes([0.55, 0.55, 0.4, 0.4],
    xlim=(xx1_dfwe, xx2_dfwe), ylim=(yy1_dfwe, yy2_dfwe))

axins_dfwe.plot(Vx_rango, ss_wea[0], linestyle = 'solid', label = r'$C_l = 0$')
axins_dfwe.plot(Vx_rango, ss_wea[1], linestyle = 'dashed', label = r'$C_l = 0.75$')
axins_dfwe.plot(Vx_rango, ss_wea[2], linestyle = 'dashdot', label = r'$C_l = 1.5$')
# axins_dfwe.fill_between(x_shadow, y_shadow, color='lightgray', alpha = 0.5)


ax_dfwe.plot(Vx_rango[1:len(Vx_rango)-1], damp_wobble[0][1:len(Vx_rango)-1], \
    'r', label = 'Lift coef = 0', linestyle = '--')
ax_dfwe.plot(Vx_rango[1:len(Vx_rango)-1], damp_wobble[1][1:len(Vx_rango)-1], \
    'b', label = 'Lift coef = 0.75', linestyle = '--')
ax_dfwe.plot(Vx_rango[1:len(Vx_rango)-1], damp_wobble[2][1:len(Vx_rango)-1], \
    'g', label = 'Lift coef = 1.5', linestyle = '--')

axins_dfwe.hlines(0, 0, 105, colors='k', linestyles='solid')
axins_dfwe.grid()
ax_dfwe.indicate_inset_zoom(axins_dfwe, edgecolor="black")

ax_dfwe.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
          ncol=3, fancybox=True, shadow=True, fontsize = '12')

plt.show()

# Damping factor wobble ----- ----- -----

# plt.plot(Vx_rango[1:len(Vx_rango)-1], damp_wobble[0][1:len(Vx_rango)-1], 'r', label = 'Lift coef = 0')
# plt.plot(Vx_rango[1:len(Vx_rango)-1], damp_wobble[1][1:len(Vx_rango)-1], 'b', label = 'Lift coef = 0.75')
# plt.plot(Vx_rango[1:len(Vx_rango)-1], damp_wobble[2][1:len(Vx_rango)-1], 'g', label = 'Lift coef = 1.5')

# plt.hlines(0, 0, 105, colors='k', linestyles='solid')
# plt.xlabel('Longitudinal speed [m/s]', fontsize=18)
# plt.ylabel('Damping factor', fontsize=18)
# plt.xlim(0, 105)
# plt.ylim(-0.15, 0.6)

# plt.grid()
# plt.show()













# ----- Weave plot -----


exit()

plt.plot(Vx_rango, ss_wea[0], 'r--', label = 'Lift coef = 0.5')
plt.plot(Vx_rango, ss_wea[1], 'b--', label = 'Lift coef = -0.5')
plt.plot(Vx_rango, ss_wea[2], 'g--', label = 'Lift coef = -1.5')
plt.text(60, -1.5, 'Weave', size=16, fontstyle='italic')

x_shadow = np.linspace(0, 105, 100)
y_shadow = np.linspace(5, 5, 100)


# Create the first legend for wobble lines
legend_wobble = plt.legend(handles=[plt.Line2D([0], [0], color='r', linestyle='-'),
                                   plt.Line2D([0], [0], color='b', linestyle='-'),
                                   plt.Line2D([0], [0], color='g', linestyle='-')],
                           labels=['Lift coef = 0', 'Lift coef = -0.75', 'Lift coef = -1.5'],
                           loc='lower right', fontsize = 15)

# # Create the second legend for weave lines
# legend_weave = plt.legend(handles=[plt.Line2D([0], [0], color='k', linestyle='--'),
#                                   plt.Line2D([0], [0], color='k', linestyle='-')],
#                           labels=['Weave', 'Wobble'],
#                           loc='lower right', fontsize = 15)

# # Add the legends to the plot
# plt.gca().add_artist(legend_wobble)  # Add the first legend back to the plot


plt.xlabel('Longitudinal speed [m/s]', fontsize=18)
plt.ylabel('Real part [1/s]', fontsize=18)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.fill_between(x_shadow, y_shadow, color='lightgray', alpha = 0.5)
plt.hlines(0, 0, 105, colors='k', linestyles='solid')
plt.text(10, 0.5, 'Unstable', size=18, fontweight='bold')
plt.text(10, -2.5, 'Stable', size=18, fontweight='bold')
plt.xlim(0, 105)
plt.ylim(-5.5, 1.5)
plt.grid()
# plt.show()

