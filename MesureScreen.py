import cv2

def get_pattern_array(pattern_image):
    # Resize pattern image on screen size
    resized_img = cv2.resize(pattern_image, dsize=(1980, 1280), interpolation=cv2.INTER_AREA)

    gray_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
    ret, binary_img = cv2.threshold(gray_img, 127, 255, cv2.THRESH_BINARY)

    height, width = binary_img.shape

    cv2.imshow("Bynary Image",binary_img)


#Main

img = cv2.imread("pattern1.jpg", cv2.IMREAD_COLOR)

get_pattern_array(img)
cv2.waitKey(0)