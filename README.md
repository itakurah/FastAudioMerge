<div id="top"></div>
<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
<!-- PROJECT LOGO -->
<br />
<div align="center">

<h3 align="center">FastAudioMerge</h3>

  <p align="center">
    Concatenate multiple audio files into a single audio file! 
    <br />
    <br />
    <a href="https://github.com/itakurah/FastAudioMerge/issues">Report Bug</a>
    ·
    <a href="https://github.com/itakurah/FastAudioMerge/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

<p align="center">
<img src="https://github.com/itakurah/FastAudioMerge/blob/main/images/screenshot.jpg"  width="40%" height="40%">
</p>
FastAudioMerge allows you to concatenate and encode multiple audio files into a single file using FFmpeg. It supports a wide range of audio formats, including mp3, aac, m4a, wav, flac, ogg, ac3, wma, aiff, mka, and mp2.

<p align="right">(<a href="#top">back to top</a>)</p>



### Built With

* [![Python][Python]][Python-url]

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started
### Prerequisites

* Python >= 3.9
* FFmpeg >= 5.1.2 (tested)

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/itakurah/FastAudioMerge
   ```
2. Install dependencies
   ```sh
   pip install -r ./requirements.txt
   ```
  
3. Download FFmpeg and copy FFmpeg.exe into the same directory as ```application.py```


4. Start FastAudioMerge `application.py`
   ```sh
   python application.py
   ```


<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Select any audio files you would like to concatenate and select the target output format.

**Note**: The encoding time depends on the file size of the input audio files.

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org/
