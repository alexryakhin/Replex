# Replex - Marketing Website

Marketing website for Replex, a comprehensive workout tracking and planning iOS app.

## About

Replex is a workout tracker and planner designed to help users achieve their fitness goals. This repository contains the marketing website that showcases the app's features, provides support resources, and links to the App Store download.

## Project Structure

```
Replex/
├── css/
│   ├── reset.css          # CSS reset styles
│   └── styles.css         # Main stylesheet with custom properties
├── favicons/              # App icons and favicons
├── images/
│   ├── icons/             # SVG icons for features
│   └── screenshots/       # App screenshots (placeholder)
├── index.html             # Main landing page
├── faq.html               # Frequently Asked Questions
├── privacy.html           # Privacy Policy
├── support.html      # Support contact page
└── terms.html              # Terms of Service
```

## Features

### App Features Highlighted
- **Comprehensive Workout Management**: Create, edit, and manage custom workout templates
- **Advanced Exercise System**: 150+ exercises across all muscle groups with muscle map visualization
- **Smart Data Management**: iCloud Sync with CloudKit for seamless cross-device synchronization
- **Calendar Integration**: Schedule workouts with EventKit integration
- **Multi-language Support**: English, German, Spanish, French, Croatian, and Russian
- **Dark Mode Support**: Automatic theme adaptation

### Website Features
- Responsive design for all devices
- Modern UI with gradient accents
- SEO-optimized meta tags
- Accessible navigation and structure
- Contact and support resources

## Tech Stack

- **HTML5**: Semantic markup
- **CSS3**: Custom properties, flexbox, grid, responsive design
- **No JavaScript**: Pure HTML/CSS implementation
- **Favicons**: Multiple sizes for various platforms

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Replex
```

2. Open `index.html` in a web browser, or serve using a local web server:

```bash
# Using Python 3
python3 -m http.server 8000

# Using Node.js http-server
npx http-server

# Using PHP
php -S localhost:8000
```

3. Navigate to `http://localhost:8000` in your browser

## Deployment

This is a static website that can be deployed to any static hosting service:

- **GitHub Pages**: Push to a repository and enable Pages in settings
- **Netlify**: Drag and drop the folder or connect to Git
- **Vercel**: Import repository or deploy via CLI
- **Cloudflare Pages**: Connect repository for automatic deployments
- **AWS S3 + CloudFront**: Upload files to S3 bucket with static hosting enabled

## App Store

Download Replex on the App Store:
- **App Store URL**: https://apps.apple.com/app/6476805884
- **Supported Platforms**: iOS 17.0+ (iPhone)

## Support

For support, questions, or feature requests:
- **Support Page**: [support.html](support.html)
- **FAQ**: [faq.html](faq.html)
- **Email**: bonney977@gmail.com
- **LinkedIn**: [xander1100001](https://www.linkedin.com/in/xander1100001)

## Legal

- [Privacy Policy](privacy.html)
- [Terms of Service](terms.html)

## Customization

### Colors
The website uses CSS custom properties defined in `css/styles.css`. The primary accent color scheme uses a blue gradient:
- `--accent-blue: #3854CF`
- `--accent-blue-dark: #082AA8`
- `--accent-gradient: linear-gradient(135deg, #3854CF 0%, #082AA8 100%)`

### Adding Screenshots
Replace placeholder divs in `index.html` with actual screenshots:
- Hero section: `images/screenshots/hero-screenshot.jpg`
- Screenshots gallery: `images/screenshots/screenshot-1.jpg`, `screenshot-2.jpg`, `screenshot-3.jpg`

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Responsive design tested on various screen sizes

## License

Copyright © 2025 Replex. All rights reserved.

---

Made with ❤️ for fitness enthusiasts
