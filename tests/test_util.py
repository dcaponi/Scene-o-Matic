import unittest

from util.util import split_string


LONG_TEST_STRING = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Leo a diam sollicitudin tempor id eu nisl nunc mi. Ullamcorper malesuada proin libero nunc consequat interdum varius sit. Tristique senectus et netus et. Malesuada pellentesque elit eget gravida cum sociis natoque penatibus. Praesent semper feugiat nibh sed pulvinar proin gravida. In ante metus dictum at. Est ultricies integer quis auctor elit sed vulputate mi. Sed enim ut sem viverra aliquet eget. Turpis massa tincidunt dui ut. Ultricies leo integer malesuada nunc vel risus. Tortor aliquam nulla facilisi cras fermentum odio. Molestie ac feugiat sed lectus vestibulum mattis. Nulla posuere sollicitudin aliquam ultrices sagittis orci a scelerisque purus. Accumsan lacus vel facilisis volutpat est velit. Egestas purus viverra accumsan in. Ac ut consequat semper viverra nam libero justo laoreet sit. Mi in nulla posuere sollicitudin aliquam ultrices sagittis. Integer vitae justo eget magna fermentum iaculis eu non diam. Dignissim diam quis enim lobortis.
Auctor neque vitae tempus quam pellentesque nec. Ac tincidunt vitae semper quis lectus nulla at volutpat diam. Molestie a iaculis at erat pellentesque adipiscing commodo elit at. Amet consectetur adipiscing elit ut aliquam purus. Libero volutpat sed cras ornare. Integer feugiat scelerisque varius morbi enim nunc faucibus. Dignissim sodales ut eu sem integer vitae justo eget magna. Aliquet enim tortor at auctor urna nunc id cursus. Massa tincidunt dui ut ornare lectus. Tempus egestas sed sed risus pretium quam vulputate. Pellentesque elit eget gravida cum sociis natoque penatibus et magnis. Morbi quis commodo odio aenean sed. Arcu non sodales neque sodales. Fringilla ut morbi tincidunt augue. At volutpat diam ut venenatis tellus in metus. Aliquam sem et tortor consequat id porta nibh venenatis cras. Ipsum a arcu cursus vitae. Diam in arcu cursus euismod quis viverra nibh cras.
Facilisis magna etiam tempor orci eu. Tincidunt ornare massa eget egestas purus viverra. Aliquam vestibulum morbi blandit cursus risus. Vestibulum sed arcu non odio euismod lacinia at quis risus. Metus vulputate eu scelerisque felis imperdiet proin. Cursus risus at ultrices mi tempus imperdiet nulla malesuada pellentesque. Vitae tempus quam pellentesque nec nam aliquam. Condimentum id venenatis a condimentum vitae. Etiam sit amet nisl purus in mollis. Ipsum dolor sit amet consectetur adipiscing elit duis tristique. Cursus eget nunc scelerisque viverra mauris in aliquam. Massa eget egestas purus viverra accumsan in nisl nisi scelerisque. Phasellus egestas tellus rutrum tellus pellentesque eu tincidunt tortor aliquam. Aliquam sem fringilla ut morbi tincidunt. Sollicitudin nibh sit amet commodo nulla facilisi. Dolor sed viverra ipsum nunc aliquet bibendum enim facilisis gravida. Imperdiet sed euismod nisi porta lorem mollis aliquam. Ut faucibus pulvinar elementum integer. Sed augue lacus viverra vitae congue eu consequat."""

class TestUtilMethods(unittest.TestCase):

    def test_split_string(self):
        small_chunks = split_string(LONG_TEST_STRING, 299)
        self.assertEqual(len(small_chunks), 11)
        for chunk in small_chunks:
            self.assertLessEqual(len(chunk.split(" ")), 300)

if __name__ == "__main__":
    unittest.main()
