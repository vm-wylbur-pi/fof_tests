import cv2
import numpy as np
import matplotlib.pyplot as plt

# To open matplotlib in interactive mode
# %matplotlib qt5
plt.ion()
 
# Load the image
#img = cv2.imread('./pics/wide-flat.jpg')
#pt_A = [306, 2742]
#pt_B = [3682, 2688]
#pt_C = [2910, 826]
#pt_D = [1014, 804]

img = cv2.imread('./pics/diamond.jpg')
pt_A = [1971, 2073]
pt_B = [3912, 1006]
pt_C = [2032, 646]
pt_D = [132, 900]

width_AD = np.sqrt(((pt_A[0] - pt_D[0]) ** 2) + ((pt_A[1] - pt_D[1]) ** 2))
width_BC = np.sqrt(((pt_B[0] - pt_C[0]) ** 2) + ((pt_B[1] - pt_C[1]) ** 2))
maxWidth = max(int(width_AD), int(width_BC))

height_AB = np.sqrt(((pt_A[0] - pt_B[0]) ** 2) + ((pt_A[1] - pt_B[1]) ** 2))
height_CD = np.sqrt(((pt_C[0] - pt_D[0]) ** 2) + ((pt_C[1] - pt_D[1]) ** 2))
maxHeight = max(int(height_AB), int(height_CD))


input_pts = np.float32([pt_A, pt_B, pt_C, pt_D])
output_pts = np.float32([[0, 0],
                         [0, maxHeight - 1],
                         [maxWidth - 1, maxHeight - 1],
                         [maxWidth - 1, 0]])

# Compute the perspective transform M
M = cv2.getPerspectiveTransform(input_pts,output_pts)
out = cv2.warpPerspective(img,M,(maxWidth, maxHeight),flags=cv2.INTER_LINEAR)

pt = np.float32([[2184, 908]])

# Apply the perspective transformation to the point
pt_warp = cv2.perspectiveTransform(pt.reshape(-1, 1, 2), M)

fix, ax = plt.subplots()

plt.xticks(np.arange(0,maxHeight, step=maxHeight/10), np.arange(0,100, step=10))
plt.yticks(np.arange(0,maxHeight, step=maxHeight/10), np.arange(0,100, step=10))

ax.imshow(out)
ax.plot(maxWidth/2,maxHeight/2,'.', color='red')

#ax.plot(pt_warp[0][0][0],pt_warp[0][0][1],'.', color='red')


#plt.imshow(out)
plt.show()