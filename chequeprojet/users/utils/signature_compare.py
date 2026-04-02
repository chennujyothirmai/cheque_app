import cv2


def compare_signatures(reference_path, cheque_path):

    ref = cv2.imread(reference_path, 0)
    che = cv2.imread(cheque_path, 0)

    sift = cv2.SIFT_create()

    kp1, des1 = sift.detectAndCompute(ref, None)
    kp2, des2 = sift.detectAndCompute(che, None)

    if des1 is None or des2 is None:
        return 0.0

    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)

    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)

    score = len(good) / max(len(matches), 1)
    return score
