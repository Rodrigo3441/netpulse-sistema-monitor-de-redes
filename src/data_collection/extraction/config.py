ANCHORS_URL = 'https://atlas.ripe.net/api/v2/anchors'
MEASUREMENTS_URL = 'https://atlas.ripe.net/api/v2/measurements'
PROBES_URL = 'https://atlas.ripe.net/api/v2/probes'

# anchor_id -> measurement_id
ANCHORS = {
    1227: 11863561,
    1526: 19649596,
    1528: 18399117,
    3146: 42167414,
    3752: 68503406,
    3931: 79420714,
    4496: 135906941
}

# measurement_id -> probe_ids
MEASUREMENT_PROBES = {
    11863561: [6251, 6316, 6349, 6398],
    19649596: [6349, 6350, 6370, 6389],
    18399117: [6349, 6389, 6358, 6382],
    42167414: [6251, 6335, 6349, 6372, 6389, 6352],
    68503406: [6328, 6333, 6349, 6364],
    79420714: [6334, 6342, 6352, 6351],
    135906941: [6414, 6424, 6443, 6438]
}