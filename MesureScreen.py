import cv2
import numpy as np

is_draw = False
is_end = False
ix , iy = 0, 0
point_list = [] # list form [x,y]

def onMouse(event, x, y, flags, param):

    global is_draw, ix, iy, is_end

    if event == cv2.EVENT_LBUTTONDOWN:
        is_draw = True
        param[y, x] = 255
        ix, iy = x, y
        #Add [x, y] array list
        point_list.append([x,y])

    elif event == cv2.EVENT_MOUSEMOVE:
        if is_draw:
            #cv2.line(param, (x, y), (ix, iy), 255, 1)
            draw_line(param, ix, iy, x, y)
            ix, iy = x, y
            #Add [x, y] array list
            #point_list.append([x, y])

    elif event == cv2.EVENT_LBUTTONUP:
        is_draw = False
        param[y, x] = 255
        #cv2.line(param, (x, y), (ix, iy), 255, 1)
        draw_line(param, ix, iy, x, y)
        #Add [x, y] array list
        #point_list.append([x, y])
        print(point_list)
        print(point_list[0][0])
        print(point_list[0][1])
        is_end = True


# drawing 8-connected line
def draw_line(param, x0, y0, x1, y1):
    dx = abs(x0 - x1)
    dy = abs(y0 - y1)

    if x0 == x1:
        if y0 == y1:
            return
        while True:
            if y0 > y1:
                param[y0,x0] = 255
                point_list.append([x0, y0])
                y0 = y0 - 1
            elif y0 < y1:
                param[y0,x0] = 255
                point_list.append([x0, y0])
                y0 = y0 + 1
            else:
                break
    elif y0 == y1:
        while True:
            if x0 > x1:
                param[y0,x0] = 255
                point_list.append([x0, y0])
                x0 = x0 - 1
            elif x0 < x1:
                param[y0,x0] = 255
                point_list.append([x0, y0])
                x0 = x0 + 1
            else:
                break
    else:
        a = (y1 - y0) / (x1 - x0)
        b = y1 - a * x1
        while True:
            if dx > dy:
                vy = a * x0 + b
                vy = round(vy)
                if x0 > x1:
                    param[vy,x0] = 255
                    point_list.append([x0, vy])
                    x0 = x0 - 1
                elif x0 < x1:
                    param[vy,x0] = 255
                    point_list.append([x0, vy])
                    x0 = x0 + 1
                else:
                    break
            else:
                vx = (y0 - b) / a
                vx = round(vx)
                if y0 > y1:
                    param[y0,vx] = 255
                    point_list.append([vx, y0])
                    y0 = y0 - 1
                elif y0 < y1:
                    param[y0,vx] = 255
                    point_list.append([vx, y0])
                    y0 = y0 + 1
                else:
                    break

def re_draw(img):
    size = len(point_list)

    for i in range(size):
        cv2.imshow('Redrawed IMG', img)
        img[point_list[i][1], point_list[i][0]] = 255
        cv2.waitKey(0)

def main():
    img = np.zeros((512, 512, 1), np.uint8)
    img2 = np.zeros((512, 512, 1), np.uint8)
    cv2.namedWindow('MakePattern')
    cv2.setMouseCallback('MakePattern', onMouse, param = img)

    while True:
        if is_end:
            re_draw(img2)

        else:
            cv2.imshow('MakePattern', img)
            k = cv2.waitKey(1) & 0xFF

            if k == 27:
                break

    cv2.destroyAllWindows()

main()