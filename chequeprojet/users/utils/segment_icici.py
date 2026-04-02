def segment_icici(img):

    H, W = img.shape[:2]
    regions = {}

    regions["ifsc"] = img[
        int(0.08 * H) : int(0.15 * H), int(0.45 * W) : int(0.85 * W)
    ]
    regions["acc_no"] = img[
        int(0.40 * H) : int(0.50 * H), int(0.12 * W) : int(0.45 * W)
    ]
    regions["legal_amount"] = img[
        int(0.32 * H) : int(0.45 * H), int(0.78 * W) : int(0.98 * W)
    ]
    regions["courtesy_amount"] = img[
        int(0.32 * H) : int(0.50 * H), int(0.78 * W) : int(0.98 * W)
    ]
    regions["signature"] = img[
        int(0.65 * H) : int(0.90 * H), int(0.70 * W) : int(0.95 * W)
    ]

    return regions
