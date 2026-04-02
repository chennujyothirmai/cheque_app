def segment_axis(img):

    H, W = img.shape[:2]
    regions = {}

    regions["ifsc"] = img[
        int(0.03 * H) : int(0.10 * H), int(0.55 * W) : int(0.95 * W)
    ]
    regions["acc_no"] = img[
        int(0.40 * H) : int(0.50 * H), int(0.15 * W) : int(0.52 * W)
    ]
    regions["legal_amount"] = img[
        int(0.32 * H) : int(0.45 * H), int(0.65 * W) : int(0.95 * W)
    ]
    regions["courtesy_amount"] = img[
        int(0.45 * H) : int(0.55 * H), int(0.65 * W) : int(0.95 * W)
    ]
    regions["signature"] = img[
        int(0.60 * H) : int(0.92 * H), int(0.60 * W) : int(0.92 * W)
    ]

    return regions
