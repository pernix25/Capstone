import cv2

hold_coords = [
    [228, 410], [464, 410], [735, 410], [958, 410], [1179, 410], [1454, 410], [1698, 410], [1932, 410], [2176, 410], [2438, 410], [2660, 410],
    [277, 680], [513, 680], [745, 680], [984, 680], [1218, 680], [1450, 680], [1689, 680], [1922, 680], [2158, 680], [2388, 680], [2626, 680],
    [325, 930], [550, 930], [776, 930], [1003, 930], [1217, 930], [1458, 930], [1720, 930], [1898, 930], [2123, 930], [2351, 930], [2583, 930],
    [366, 1166], [585, 1166], [814, 1166], [1037, 1166], [1240, 1166], [1464, 1166], [1674, 1166], [1891, 1166], [2120, 1166], [2325, 1166], [2545, 1166],
    [407, 1374], [624, 1374], [839, 1374], [1038, 1374], [1250, 1374], [1458, 1374], [1661, 1374], [1872, 1374], [2071, 1374], [2298, 1374], [2495, 1374],
    [442, 1576], [658, 1576], [854, 1585], [1059, 1582], [1262, 1582], [1460, 1585], [1660, 1585], [1859, 1578], [2054, 1581], [2268, 1573], [2470, 1570],
    [487, 1783], [688, 1783], [880, 1783], [1077, 1790], [1277, 1785], [1461, 1784], [1655, 1789], [1844, 1780], [2041, 1774], [2236, 1774], [2428, 1776],
    [510, 1959], [713, 1964], [900, 1957], [1094, 1956], [1280, 1960], [1462, 1952], [1644, 1945], [1831, 1952], [2017, 1946], [2217, 1953], [2399, 1953],
    [555, 2118], [735, 2122], [917, 2114], [1103, 2112], [1283, 2124], [1470, 2112], [1652, 2117], [1832, 2117], [2007, 2117], [2185, 2117], [2376, 2117],
    [553, 2248], [758, 2273], [934, 2270], [1115, 2269], [1290, 2260], [1467, 2260], [1635, 2260], [1814, 2270], [1998, 2260], [2158, 2258], [2347, 2270],
    [593, 2434], [778, 2421], [949, 2417], [1127, 2409], [1293, 2403], [1464, 2405], [1634, 2405], [1804, 2403], [1975, 2400], [2151, 2404], [2328, 2407],
    [630, 2551], [798, 2546], [967, 2546], [1133, 2548], [1302, 2547], [1467, 2544], [1634, 2541], [1799, 2541], [1935, 2526], [2134, 2544], [2297, 2545],
    [657, 2695], [820, 2695], [983, 2690], [1144, 2681], [1306, 2689], [1468, 2680], [1624, 2692], [1786, 2688], [1949, 2689], [2116, 2681], [2258, 2672],
    [675, 2826], [838, 2821], [993, 2811], [1157, 2812], [1314, 2809], [1469, 2817], [1617, 2814], [1787, 2805], [1944, 2809], [2103, 2808], [2258, 2808],
    [697, 2931], [855, 2932], [1012, 2928], [1163, 2928], [1304, 2937], [1470, 2935], [1624, 2928], [1781, 2935], [1932, 2926], [2087, 2924], [2248, 2925],
    [718, 3047], [865, 3047], [1017, 3040], [1174, 3044], [1318, 3039], [1469, 3040], [1618, 3037], [1772, 3034], [1921, 3031], [2072, 3035], [2220, 3034],
    [732, 3156], [882, 3148], [1013, 3163], [1173, 3146], [1324, 3141], [1478, 3145], [1624, 3142], [1764, 3144], [1922, 3143], [2060, 3140], [2208, 3139],
    [754, 3248], [897, 3251], [1042, 3246], [1183, 3246], [1325, 3250], [1472, 3243], [1625, 3244], [1756, 3249], [1902, 3240], [2047, 3240], [2186, 3240]
]

def draw(image, coord, radius):
    # Define circle parameters
    center_coordinates = (coord[0], coord[1])  # (x, y) coordinates of the center
    radius = radius                 # Radius of the circle
    color = (0, 255, 0)              # Color in BGR format (Green in this case)
    thickness = 5                    # Thickness of the circle outline (-1 for filled)

    # Draw the circle
    return cv2.circle(image, center_coordinates, radius, color, thickness)

# Load the image
image = cv2.imread("moonBoard.jpg")  # Replace with your image path
image_with_circle = image

radius_count = 0
radius = 125
for coord in hold_coords:
    if radius_count % 66 == 0:
        radius -= 25
    image_with_circle = draw(image_with_circle, coord, radius)
    radius_count += 1

# Display the image
cv2.imshow("Image with Circle", image_with_circle)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Save the modified image (optional)
cv2.imwrite("labeled.jpg", image_with_circle)
