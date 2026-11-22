import io
import json
import unittest

from tools.ultimate_client_audit import MARKERS, scan_source_map, scan_stream


class UltimateClientAuditTests(unittest.TestCase):
    def test_finds_markers_split_across_chunks(self):
        payload = b"prefix Minecraft 1.6.4 middle Forge Mod Loader suffix"
        result = scan_stream(io.BytesIO(payload), chunk_size=11)
        self.assertTrue(result["minecraft_1_6_4"])
        self.assertTrue(result["forge_mod_loader"])

    def test_reports_absent_markers_as_false(self):
        result = scan_stream(io.BytesIO(b"plain unrelated file"), chunk_size=4)
        self.assertTrue(all(value is False for value in result.values()))

    def test_marker_catalog_is_nonempty(self):
        self.assertTrue(MARKERS)
        self.assertTrue(all(values for values in MARKERS.values()))

    def test_rejects_zero_chunk_size(self):
        with self.assertRaises(ValueError):
            scan_stream(io.BytesIO(b"anything"), chunk_size=0)

    def test_source_map_reports_forge_and_eagler_layers(self):
        source_map = {
            "sources": [
                "net/minecraft/network/packet/Packet250CustomPayload.java",
                "cpw/mods/fml/common/network/FMLPacket.java",
                "net/lax1dude/eaglercraft/socket/EaglerNetworkManagerClientWS.java",
                "appeng/common/network/AppEngPacket.java",
            ]
        }
        result = scan_source_map(io.StringIO(json.dumps(source_map)))
        self.assertIn(
            "cpw/mods/fml/common/network/FMLPacket.java",
            result["groups"]["forge_fml_handshake_layer"]["present"],
        )
        self.assertIn(
            "net/lax1dude/eaglercraft/socket/EaglerNetworkManagerClientWS.java",
            result["groups"]["eagler_websocket_client_layer"]["present"],
        )
        self.assertIn("appeng/common/network/AppEngPacket.java", result["mod_network_classes"])

    def test_source_map_rejects_invalid_sources_type(self):
        with self.assertRaises(ValueError):
            scan_source_map(io.StringIO('{"sources": "not-an-array"}'))


if __name__ == "__main__":
    unittest.main()
