import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
import tempfile
import os
from main import InstagramDownloaderApp


class TestInstagramDownloaderApp(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Prevent the Tk window from appearing
        self.app = InstagramDownloaderApp(self.root)

    def tearDown(self):
        self.root.destroy()

    @patch('main.instaloader.Instaloader')
    @patch('main.instaloader.Post.from_shortcode')
    @patch('main.requests.get')
    def test_download_video(self, mock_requests_get, mock_from_shortcode, mock_instaloader):
        # Setting up mocks
        mock_loader = MagicMock()
        mock_instaloader.return_value = mock_loader
        mock_post = MagicMock()
        mock_post.video_url = 'http://example.com/video.mp4'
        mock_from_shortcode.return_value = mock_post

        # Prepare a mock response for requests.get
        mock_response = MagicMock()
        mock_response.headers = {'content-length': '12345'}
        mock_response.iter_content.return_value = [b'chunk1', b'chunk2']
        mock_requests_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as temp_dir:
            url = 'http://instagram.com/p/shortcode/'
            self.app.download_video(url, temp_dir)

            video_filename = os.path.join(temp_dir, 'shortcode.mp4')

            self.assertTrue(os.path.exists(video_filename),
                            "Video file was not created")

        if os.path.exists(video_filename):
            os.remove(video_filename)

    @patch('tkinter.messagebox.showinfo')
    @patch('tkinter.messagebox.showerror')
    @patch('main.filedialog.askdirectory')
    def test_browse_folder(self, mock_askdirectory, mock_showerror, mock_showinfo):
        mock_showinfo.return_value = None
        mock_showerror.return_value = None
        mock_askdirectory.return_value = '/mock/folder'
        self.app.browse_folder()
        self.assertEqual(self.app.folder_entry.get(), '/mock/folder')

    @patch('tkinter.messagebox.showerror')
    def test_start_download_no_url_or_folder(self, mock_showerror):
        mock_showerror.return_value = None
        self.app.url_entry.delete(0, tk.END)
        self.app.folder_entry.delete(0, tk.END)
        self.app.start_download()
        mock_showerror.assert_called_with(
            "Error", "Please enter the URL and select a download folder.")

    @patch('main.requests.get')
    @patch('main.instaloader.Instaloader')
    @patch('main.instaloader.Post.from_shortcode')
    def test_download_video_error_handling(self, mock_from_shortcode, mock_instaloader, mock_requests_get):
        mock_requests_get.side_effect = Exception("Download failed")

        with tempfile.TemporaryDirectory() as temp_dir:
            url = 'http://instagram.com/p/shortcode/'
            self.app.download_video(url, temp_dir)

            video_filename = os.path.join(temp_dir, 'shortcode.mp4')
            self.assertFalse(os.path.exists(video_filename),
                             "Video file was created despite error")


if __name__ == '__main__':
    unittest.main()
