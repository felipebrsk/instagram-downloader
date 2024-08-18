# __tests__/test_main.py
import unittest
from unittest.mock import patch, MagicMock
import os
import tkinter as tk
import tempfile
from main import InstagramDownloaderApp


class TestInstagramDownloaderApp(unittest.TestCase):

    def setUp(self):
        # Create a Tk root window instance for testing
        self.root = tk.Tk()
        self.app = InstagramDownloaderApp(self.root)

    def tearDown(self):
        # Destroy the Tk root window after tests
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

        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            url = 'http://instagram.com/p/shortcode/'
            self.app.download_video(url, temp_dir)

            # Check the expected file path
            video_filename = os.path.join(temp_dir, 'shortcode.mp4')

            # Verify if the video file was created
            self.assertTrue(os.path.exists(video_filename),
                            "Video file was not created")

        # Clean up
        if os.path.exists(video_filename):
            os.remove(video_filename)

    @patch('main.filedialog.askdirectory')
    def test_browse_folder(self, mock_askdirectory):
        mock_askdirectory.return_value = '/mock/folder'
        self.app.browse_folder()
        self.assertEqual(self.app.folder_entry.get(), '/mock/folder')

    @patch('main.messagebox.showerror')
    def test_start_download_no_url_or_folder(self, mock_showerror):
        self.app.url_entry.delete(0, tk.END)
        self.app.folder_entry.delete(0, tk.END)
        self.app.start_download()
        mock_showerror.assert_called_with(
            "Error", "Please enter the URL and select a download folder.")

    @patch('main.requests.get')
    @patch('main.instaloader.Instaloader')
    @patch('main.instaloader.Post.from_shortcode')
    def test_download_video_error_handling(self, mock_from_shortcode, mock_instaloader, mock_requests_get):
        # Setup mocks to raise an exception
        mock_requests_get.side_effect = Exception("Download failed")

        with tempfile.TemporaryDirectory() as temp_dir:
            url = 'http://instagram.com/p/shortcode/'
            self.app.download_video(url, temp_dir)

            # Ensure no video file was created
            video_filename = os.path.join(temp_dir, 'shortcode.mp4')
            self.assertFalse(os.path.exists(video_filename),
                             "Video file was created despite error")


if __name__ == '__main__':
    unittest.main()
