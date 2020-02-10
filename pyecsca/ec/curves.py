import json
from os.path import join
from typing import Mapping, Any

from pkg_resources import resource_listdir, resource_isdir, resource_stream
from public import public

from .coordinates import AffineCoordinateModel
from .curve import EllipticCurve
from .mod import Mod
from .model import (ShortWeierstrassModel, MontgomeryModel, TwistedEdwardsModel,
                    EdwardsModel, CurveModel)
from .params import DomainParameters
from .point import Point, InfinityPoint

SHORT_WEIERSTRASS: Mapping[str, Mapping[str, Any]] = {
    "brainpoolP160r1": {
        "p": 0xE95E4A5F737059DC60DFC7AD95B3D8139515620F,
        "a": 0x340E7BE2A280EB74E2BE61BADA745D97E8F7C300,
        "b": 0x1E589A8595423412134FAA2DBDEC95C8D8675E58,
        "g": (0xBED5AF16EA3F6A4F62938C4631EB5AF7BDBCDBC3,
              0x1667CB477A1A8EC338F94741669C976316DA6321),
        "n": 0xE95E4A5F737059DC60DF5991D45029409E60FC09,
        "h": 0x1},
    "brainpoolP192r1": {
        "p": 0xC302F41D932A36CDA7A3463093D18DB78FCE476DE1A86297,
        "a": 0x6A91174076B1E0E19C39C031FE8685C1CAE040E5C69A28EF,
        "b": 0x469A28EF7C28CCA3DC721D044F4496BCCA7EF4146FBF25C9,
        "g": (0xC0A0647EAAB6A48753B033C56CB0F0900A2F5C4853375FD6,
              0x14B690866ABD5BB88B5F4828C1490002E6773FA2FA299B8F),
        "n": 0xC302F41D932A36CDA7A3462F9E9E916B5BE8F1029AC4ACC1,
        "h": 0x1},
    "brainpoolP224r1": {
        "p": 0xD7C134AA264366862A18302575D1D787B09F075797DA89F57EC8C0FF,
        "a": 0x68A5E62CA9CE6C1C299803A6C1530B514E182AD8B0042A59CAD29F43,
        "b": 0x2580F63CCFE44138870713B1A92369E33E2135D266DBB372386C400B,
        "g": (0x0D9029AD2C7E5CF4340823B2A87DC68C9E4CE3174C1E6EFDEE12C07D,
              0x58AA56F772C0726F24C6B89E4ECDAC24354B9E99CAA3F6D3761402CD),
        "n": 0xD7C134AA264366862A18302575D0FB98D116BC4B6DDEBCA3A5A7939F,
        "h": 0x1},
    "brainpoolP256r1": {
        "p": 0xA9FB57DBA1EEA9BC3E660A909D838D726E3BF623D52620282013481D1F6E5377,
        "a": 0x7D5A0975FC2C3057EEF67530417AFFE7FB8055C126DC5C6CE94A4B44F330B5D9,
        "b": 0x26DC5C6CE94A4B44F330B5D9BBD77CBF958416295CF7E1CE6BCCDC18FF8C07B6,
        "g": (0x8BD2AEB9CB7E57CB2C4B482FFC81B7AFB9DE27E1E3BD23C23A4453BD9ACE3262,
              0x547EF835C3DAC4FD97F8461A14611DC9C27745132DED8E545C1D54C72F046997),
        "n": 0xA9FB57DBA1EEA9BC3E660A909D838D718C397AA3B561A6F7901E0E82974856A7,
        "h": 0x1},
    "brainpoolP320r1": {
        "p": 0xD35E472036BC4FB7E13C785ED201E065F98FCFA6F6F40DEF4F92B9EC7893EC28FCD412B1F1B32E27,
        "a": 0x3EE30B568FBAB0F883CCEBD46D3F3BB8A2A73513F5EB79DA66190EB085FFA9F492F375A97D860EB4,
        "b": 0x520883949DFDBC42D3AD198640688A6FE13F41349554B49ACC31DCCD884539816F5EB4AC8FB1F1A6,
        "g": (
            0x43BD7E9AFB53D8B85289BCC48EE5BFE6F20137D10A087EB6E7871E2A10A599C710AF8D0D39E20611,
            0x14FDD05545EC1CC8AB4093247F77275E0743FFED117182EAA9C77877AAAC6AC7D35245D1692E8EE1),
        "n": 0xD35E472036BC4FB7E13C785ED201E065F98FCFA5B68F12A32D482EC7EE8658E98691555B44C59311,
        "h": 0x1},
    "brainpoolP384r1": {
        "p": 0x8CB91E82A3386D280F5D6F7E50E641DF152F7109ED5456B412B1DA197FB71123ACD3A729901D1A71874700133107EC53,
        "a": 0x7BC382C63D8C150C3C72080ACE05AFA0C2BEA28E4FB22787139165EFBA91F90F8AA5814A503AD4EB04A8C7DD22CE2826,
        "b": 0x04A8C7DD22CE28268B39B55416F0447C2FB77DE107DCD2A62E880EA53EEB62D57CB4390295DBC9943AB78696FA504C11,
        "g": (
            0x1D1C64F068CF45FFA2A63A81B7C13F6B8847A3E77EF14FE3DB7FCAFE0CBD10E8E826E03436D646AAEF87B2E247D4AF1E,
            0x8ABE1D7520F9C2A45CB1EB8E95CFD55262B70B29FEEC5864E19C054FF99129280E4646217791811142820341263C5315),
        "n": 0x8CB91E82A3386D280F5D6F7E50E641DF152F7109ED5456B31F166E6CAC0425A7CF3AB6AF6B7FC3103B883202E9046565,
        "h": 0x1},
    "brainpoolP512r1": {
        "p": 0xAADD9DB8DBE9C48B3FD4E6AE33C9FC07CB308DB3B3C9D20ED6639CCA703308717D4D9B009BC66842AECDA12AE6A380E62881FF2F2D82C68528AA6056583A48F3,
        "a": 0x7830A3318B603B89E2327145AC234CC594CBDD8D3DF91610A83441CAEA9863BC2DED5D5AA8253AA10A2EF1C98B9AC8B57F1117A72BF2C7B9E7C1AC4D77FC94CA,
        "b": 0x3DF91610A83441CAEA9863BC2DED5D5AA8253AA10A2EF1C98B9AC8B57F1117A72BF2C7B9E7C1AC4D77FC94CADC083E67984050B75EBAE5DD2809BD638016F723,
        "g": (
            0x81AEE4BDD82ED9645A21322E9C4C6A9385ED9F70B5D916C1B43B62EEF4D0098EFF3B1F78E2D0D48D50D1687B93B97D5F7C6D5047406A5E688B352209BCB9F822,
            0x7DDE385D566332ECC0EABFA9CF7822FDF209F70024A57B1AA000C55B881F8111B2DCDE494A5F485E5BCA4BD88A2763AED1CA2B2FA8F0540678CD1E0F3AD80892),
        "n": 0xAADD9DB8DBE9C48B3FD4E6AE33C9FC07CB308DB3B3C9D20ED6639CCA70330870553E5C414CA92619418661197FAC10471DB1D381085DDADDB58796829CA90069,
        "h": 0x1},
    "secp128r1": {
        "p": 0xfffffffdffffffffffffffffffffffff,
        "a": 0xfffffffdfffffffffffffffffffffffc,
        "b": 0xe87579c11079f43dd824993c2cee5ed3,
        "g": (0x161ff7528b899b2d0c28607ca52c5b86,
              0xcf5ac8395bafeb13c02da292dded7a83),
        "n": 0xfffffffe0000000075a30d1b9038a115,
        "h": 0x1},
    "secp128r2": {
        "p": 0xfffffffdffffffffffffffffffffffff,
        "a": 0xd6031998d1b3bbfebf59cc9bbff9aee1,
        "b": 0x5eeefca380d02919dc2c6558bb6d8a5d,
        "g": (0x7b6aa5d85e572983e6fb32a7cdebc140,
              0x27b6916a894d3aee7106fe805fc34b44),
        "n": 0x3fffffff7fffffffbe0024720613b5a3,
        "h": 0x4},
    "secp160k1": {
        "p": 0xfffffffffffffffffffffffffffffffeffffac73,
        "a": 0x0000000000000000000000000000000000000000,
        "b": 0x0000000000000000000000000000000000000007,
        "g": (0x3b4c382ce37aa192a4019e763036f4f5dd4d7ebb,
              0x938cf935318fdced6bc28286531733c3f03c4fee),
        "n": 0x0100000000000000000001b8fa16dfab9aca16b6b3,
        "h": 0x1},
    "secp160r1": {
        "p": 0xffffffffffffffffffffffffffffffff7fffffff,
        "a": 0xffffffffffffffffffffffffffffffff7ffffffc,
        "b": 0x1c97befc54bd7a8b65acf89f81d4d4adc565fa45,
        "g": (0x4a96b5688ef573284664698968c38bb913cbfc82,
              0x23a628553168947d59dcc912042351377ac5fb32),
        "n": 0x0100000000000000000001f4c8f927aed3ca752257,
        "h": 0x1},
    "secp160r2": {
        "p": 0xfffffffffffffffffffffffffffffffeffffac73,
        "a": 0xfffffffffffffffffffffffffffffffeffffac70,
        "b": 0xb4e134d3fb59eb8bab57274904664d5af50388ba,
        "g": (0x52dcb034293a117e1f4ff11b30f7199d3144ce6d,
              0xfeaffef2e331f296e071fa0df9982cfea7d43f2e),
        "n": 0x0100000000000000000000351ee786a818f3a1a16b,
        "h": 0x1},
    "secp192r1": {
        "p": 0xfffffffffffffffffffffffffffffffeffffffffffffffff,
        "a": 0xfffffffffffffffffffffffffffffffefffffffffffffffc,
        "b": 0x64210519e59c80e70fa7e9ab72243049feb8deecc146b9b1,
        "g": (0x188da80eb03090f67cbf20eb43a18800f4ff0afd82ff1012,
              0x07192b95ffc8da78631011ed6b24cdd573f977a11e794811),
        "n": 0xffffffffffffffffffffffff99def836146bc9b1b4d22831,
        "h": 0x1},
    "secp224r1": {
        "p": 0xffffffffffffffffffffffffffffffff000000000000000000000001,
        "a": 0xfffffffffffffffffffffffffffffffefffffffffffffffffffffffe,
        "b": 0xb4050a850c04b3abf54132565044b0b7d7bfd8ba270b39432355ffb4,
        "g": (0xb70e0cbd6bb4bf7f321390b94a03c1d356c21122343280d6115c1d21,
              0xbd376388b5f723fb4c22dfe6cd4375a05a07476444d5819985007e34),
        "n": 0xffffffffffffffffffffffffffff16a2e0b8f03e13dd29455c5c2a3d,
        "h": 0x1},
    "secp256r1": {
        "p": 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff,
        "a": 0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc,
        "b": 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b,
        "g": (0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
              0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5),
        "n": 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551,
        "h": 0x1},
    "secp384r1": {
        "p": 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000ffffffff,
        "a": 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000fffffffc,
        "b": 0xb3312fa7e23ee7e4988e056be3f82d19181d9c6efe8141120314088f5013875ac656398d8a2ed19d2a85c8edd3ec2aef,
        "g": (
            0xaa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7,
            0x3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147ce9da3113b5f0b8c00a60b1ce1d7e819d7a431d7c90ea0e5f),
        "n": 0xffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973,
        "h": 0x1},
    "secp521r1": {
        "p": 0x000001ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff,
        "a": 0x000001fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffc,
        "b": 0x00000051953eb9618e1c9a1f929a21a0b68540eea2da725b99b315f3b8b489918ef109e156193951ec7e937b1652c0bd3bb1bf073573df883d2c34f1ef451fd46b503f00,
        "g": (
            0x000000c6858e06b70404e9cd9e3ecb662395b4429c648139053fb521f828af606b4d3dbaa14b5e77efe75928fe1dc127a2ffa8de3348b3c1856a429bf97e7e31c2e5bd66,
            0x0000011839296a789a3bc0045c8a5fb42c7d1bd998f54449579b446817afbd17273e662c97ee72995ef42640c550b9013fad0761353c7086a272c24088be94769fd16650),
        "n": 0x000001fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffa51868783bf2f966b7fcc0148f709a5d03bb5c9b8899c47aebb6fb71e91386409,
        "h": 0x1}}

MONTGOMERY: Mapping[str, Mapping[str, Any]] = {
    "curve25519": {
        "p": 0x7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffed,
        "a": 486662,
        "b": 1,
        "x": 9,
        "z": 1,
        "n": 0x1000000000000000000000000000000014DEF9DEA2F79CD65812631A5CF5D3ED,
        "h": 2
    }
}

EDWARDS: Mapping[str, Mapping[str, Any]] = {
    "ed448": {
        "p": 2 ** 448 - 2 ** 224 - 1,
        "c": 1,
        "d": 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffffffffffffffffffffffffffffffffffffffffffffffff6756,
        "g": (
            0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa955555555555555555555555555555555555555555555555555555555,
            0xae05e9634ad7048db359d6205086c2b0036ed7a035884dd7b7e36d728ad8c4b80d6565833a2a3098bbbcb2bed1cda06bdaeafbcdea9386ed),
        "n": 0x3fffffffffffffffffffffffffffffffffffffffffffffffffffffff7cca23e9c44edb49aed63690216cc2728dc58f552378c292ab5844f3,
        "h": 4
    }
}

TWISTED_EDWARDS: Mapping[str, Mapping[str, Any]] = {
    "ed25519": {
        "p": 2 ** 255 - 19,
        "d": 0x52036cee2b6ffe738cc740797779e89800700a4d4141d8ab75eb4dca135978a3,
        "a": -1,
        "g": (0x216936d3cd6e53fec0a4e231fdd6dc5c692cc7609525a7b2c9562d608f25d51a,
              0x6666666666666666666666666666666666666666666666666666666666666658),
        "n": 0x1000000000000000000000000000000014def9dea2f79cd65812631a5cf5d3ed,
        "h": 2
    }
}


@public
def get_params(category: str, name: str, coords: str) -> DomainParameters:
    """
    Retrieve a curve from a set of stored parameters. Uses the std-curves database at
    https://github.com/J08nY/std-curves.

    :param category: The category of the curve.
    :param name: The name of the curve.
    :param coords: The name of the coordinate system to use.
    :return: The curve.
    """
    listing = resource_listdir(__name__, "std")
    categories = list(entry for entry in listing if resource_isdir(__name__, join("std", entry)))
    if category not in categories:
        raise ValueError("Category {} not found.".format(category))
    json_path = join("std", category, "curves.json")
    with resource_stream(__name__, json_path) as f:
        category_json = json.load(f)
    for curve in category_json["curves"]:
        if curve["name"] == name:
            break
    else:
        raise ValueError("Curve {} not found in category {}.".format(name, category))
    if curve["field"]["type"] == "Binary":
        raise ValueError("Binary field curves are currently not supported.")

    model: CurveModel
    field = int(curve["field"]["p"], 16)
    order = int(curve["order"], 16)
    cofactor = int(curve["cofactor"], 16)
    if curve["form"] == "Weierstrass":
        model = ShortWeierstrassModel()
        param_names = ["a", "b"]
    elif curve["form"] == "Montgomery":
        model = MontgomeryModel()
        param_names = ["a", "b"]
    elif curve["form"] == "Edwards":
        model = EdwardsModel()
        param_names = ["c", "d"]
    elif curve["form"] == "TwistedEdwards":
        model = TwistedEdwardsModel()
        param_names = ["a", "d"]
    else:
        raise ValueError("Unknown curve model.")
    if coords not in model.coordinates:
        raise ValueError("Coordinate model not supported for curve.")
    coord_model = model.coordinates[coords]
    params = {name: int(curve["params"][name], 16) for name in param_names}
    elliptic_curve = EllipticCurve(model, coord_model, field, params)
    affine = Point(AffineCoordinateModel(model), x=Mod(int(curve["generator"]["x"], 16), field),
                   y=Mod(int(curve["generator"]["y"], 16), field))
    generator = Point.from_affine(coord_model, affine)
    return DomainParameters(elliptic_curve, generator, InfinityPoint(coord_model), order, cofactor)
