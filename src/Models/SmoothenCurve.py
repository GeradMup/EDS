
import numpy as np
import numpy as np
from scipy.interpolate import make_interp_spline
import matplotlib.pyplot as plt
 
# Dataset
x = np.array([1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.01, 0.005, 0.00134])
y = np.array([0.658, 0.685, 0.731, 0.781, 0.832, 0.883, 0.939, 0.997, 1.116, 1.528, 1.614, 1.707, 1.811, 1.92, 2.025, 2.102, 2.098, 1.929, 1.303, 0.721, 0.2])

x = np.flip(x)
y = np.flip(y)

X_Y_Spline = make_interp_spline(x, y)
 
# Returns evenly spaced numbers
# over a specified interval.
X_ = np.linspace(x.min(), x.max(), 500)
Y_ = X_Y_Spline(X_)

print(len(X_))
print(len(Y_))
 
# Plotting the Graph
plt.plot(X_, Y_)
#plt.plot(x,y)
plt.title("Plot Smooth Curve Using the scipy.interpolate.make_interp_spline() Class")
plt.xlabel("X")
plt.ylabel("Y")
plt.show()
