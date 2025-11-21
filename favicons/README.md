# Favicons Directory

Place your app icon files here for use as:
- Browser tab favicon (small icon in browser tabs)
- Header logo (icon next to app title)
- Mobile home screen icons

## Required Files

### For Browser Tab (Favicon)
- **favicon.ico** - 16x16 or 32x32px, ICO format (for older browsers)
- **favicon-16x16.png** - 16x16px PNG
- **favicon-32x32.png** - 32x32px PNG

### For Mobile Devices
- **apple-touch-icon.png** - 180x180px PNG (for iOS home screen)
- **android-chrome-192x192.png** - 192x192px PNG (for Android)
- **android-chrome-512x512.png** - 512x512px PNG (for Android)

### For Header Logo
- **logo.svg** - SVG format (recommended, scales perfectly)
- **OR logo.png** - PNG format, 32x32px or larger

## Quick Setup

### Option 1: Use Your App Icon
If you have your app icon from Xcode:
1. Export your app icon at these sizes
2. Name them according to the list above
3. Place them in this `favicons/` directory

### Option 2: Generate from Single Image
If you have one high-resolution icon (1024x1024px recommended):
1. Use an online tool like [RealFaviconGenerator](https://realfavicongenerator.net/)
2. Upload your icon
3. Download the generated files
4. Place them in this `favicons/` directory

### Option 3: Use SVG (Modern Approach)
For modern browsers, you can use just an SVG:
1. Place your icon as `logo.svg` in this directory
2. The HTML will automatically use it for both favicon and header logo

## File Structure

```
favicons/
├── favicon.ico              ← Browser tab icon (ICO format)
├── favicon-16x16.png        ← Small browser icon
├── favicon-32x32.png        ← Standard browser icon
├── apple-touch-icon.png     ← iOS home screen icon (180x180)
├── android-chrome-192x192.png ← Android icon
├── android-chrome-512x512.png ← Android icon (large)
└── logo.svg                 ← Header logo (SVG recommended)
```

## After Adding Files

1. **For Header Logo**: Uncomment the `<img>` tag in the header of all HTML files:
   ```html
   <!-- Change from: -->
   <!-- <img src="favicons/logo.svg" alt="Replex Logo"> -->
   
   <!-- To: -->
   <img src="favicons/logo.svg" alt="Replex Logo">
   ```

2. **Test**: Open your site in a browser and check:
   - Browser tab shows your favicon
   - Header shows your logo next to "Replex" text

## Tips

- **SVG is best** for the header logo (scales perfectly, small file size)
- **PNG is fine** if you don't have SVG (use 32x32px or 64x64px)
- **ICO format** can be generated from PNG using online converters
- Keep file sizes small for faster loading

