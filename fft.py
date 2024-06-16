# Took code from https://pythonnumericalmethods.studentorg.berkeley.edu/notebooks/chapter24.03-Fast-Fourier-Transform.html
# Tweaked it a bit, but haven't understood much...
import matplotlib.pyplot as plt
import numpy as np

def FFT(x):
    """
    A recursive implementation of 
    the 1D Cooley-Tukey FFT, the 
    input should have a length of 
    power of 2. 
    """
    N = len(x)
    
    if N == 1:
        return x
    else:
        X_even = FFT(x[::2])
        X_odd = FFT(x[1::2])
        factor = \
          np.exp(-2j*np.pi*np.arange(N)/ N)
        
        X = np.concatenate(\
            [X_even+factor[:int(N/2)]*X_odd,
             X_even+factor[int(N/2):]*X_odd])
        return X

sample_rate = 128
sample_interval = 1.0/sample_rate
t = np.arange(0,1,sample_interval)

input_freqs = [[2., 3], [4, 1], [7, .5]]
x = 0
for (freq, amplitude) in input_freqs:
    x += amplitude*np.sin(2*np.pi*freq*t)


plt.figure(figsize = (8, 6))
plt.plot(t, x, 'r')
plt.ylabel('Amplitude')

# plt.show()

X=FFT(x)

# calculate the frequency
N = len(X)
x = np.arange(N)
T = N/sample_rate
freq = x/T

plt.figure(figsize = (12, 6))
plt.subplot(121)
plt.stem(freq, abs(X), 'b', \
         markerfmt=" ", basefmt="-b")
plt.xlabel('Freq (Hz)')
plt.ylabel('FFT Amplitude |X(freq)|')

# Get the one-sided spectrum
n_oneside = N//2
# get the one side frequency
f_oneside = freq[:n_oneside]

# normalize the amplitude
X_oneside =X[:n_oneside]/n_oneside
found_freq = []
for i,ampli in enumerate(abs(X_oneside)):
    if ampli.real+ampli.imag > .1:
        found_freq.append([freq[i], ampli])

for i in range(len(found_freq)):
    print(found_freq[i], input_freqs[i])

plt.subplot(122)
plt.stem(f_oneside, abs(X_oneside), 'b', \
         markerfmt=" ", basefmt="-b")
plt.xlabel('Freq (Hz)')
plt.ylabel('Normalized FFT Amplitude |X(freq)|')
plt.tight_layout()
plt.show()