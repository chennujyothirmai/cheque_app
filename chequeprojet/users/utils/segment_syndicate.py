def segment_syndicate(img):

    H, W = img.shape[:2]
    regions = {}

    regions["ifsc"] = img[
        int(0.02 * H) : int(0.08 * H), int(0.55 * W) : int(0.95 * W)
    ]
    regions["acc_no"] = img[
        int(0.32 * H) : int(0.42 * H), int(0.15 * W) : int(0.60 * W)
    ]
    regions["legal_amount"] = img[
        int(0.32 * H) : int(0.42 * H), int(0.65 * W) : int(0.90 * W)
    ]
    regions["courtesy_amount"] = img[
        int(0.41 * H) : int(0.53 * H), int(0.65 * W) : int(0.90 * W)
    ]
    regions["signature"] = img[
        int(0.65 * H) : int(0.88 * H), int(0.60 * W) : int(0.92 * W)
    ]

    return regions
