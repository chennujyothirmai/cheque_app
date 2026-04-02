def segment_canara(img):

    H, W = img.shape[:2]
    regions = {}

    regions["ifsc"] = img[
        int(0.04 * H) : int(0.12 * H), int(0.60 * W) : int(0.95 * W)
    ]
    regions["acc_no"] = img[
        int(0.35 * H) : int(0.45 * H), int(0.15 * W) : int(0.55 * W)
    ]
    regions["legal_amount"] = img[
        int(0.32 * H) : int(0.45 * H), int(0.70 * W) : int(0.95 * W)
    ]
    regions["courtesy_amount"] = img[
        int(0.42 * H) : int(0.55 * H), int(0.70 * W) : int(0.95 * W)
    ]
    regions["signature"] = img[
        int(0.60 * H) : int(0.92 * H), int(0.60 * W) : int(0.92 * W)
    ]

    return regions
