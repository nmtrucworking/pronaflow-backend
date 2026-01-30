# Typography System Documentation

## Overview
Hệ thống Typography thống nhất cho toàn bộ frontend, đảm bảo tính nhất quán về font-size, line-height và spacing.

## Font Scale

### Base Sizes (với rem units)
- **micro**: 10px (0.625rem) - Badges, tiny labels
- **caption**: 11px (0.6875rem) - Captions, metadata
- **xs**: 12px (0.75rem) - Small UI elements
- **sm**: 14px (0.875rem) - Secondary text, inputs
- **body**: 15px (0.9375rem) - Main body text
- **base**: 16px (1rem) - Default text size
- **subtitle**: 17px (1.0625rem) - Subtitles, important body
- **lg**: 18px (1.125rem) - Large text
- **xl**: 20px (1.25rem) - Section titles
- **2xl**: 24px (1.5rem) - Page headings
- **3xl**: 30px (1.875rem) - Main titles
- **4xl**: 36px (2.25rem) - Display text
- **5xl**: 48px (3rem) - Hero text
- **6xl**: 60px (3.75rem) - Large display

## Usage

### 1. Component Approach (Recommended)
```tsx
import { Typography } from '@/components/ui/Typography';

// Semantic typography components
<Typography.Display>Hero Heading</Typography.Display>
<Typography.Title>Page Title</Typography.Title>
<Typography.Headline>Section Title</Typography.Headline>
<Typography.Body>Main content text</Typography.Body>
<Typography.Caption>Small descriptive text</Typography.Caption>
<Typography.Overline>BADGE TEXT</Typography.Overline>
```

### 2. Utility Classes Approach
```tsx
// Direct Tailwind classes
<h1 className="text-display">Hero Heading</h1>
<p className="text-body">Main content</p>
<span className="text-caption">Caption text</span>
<span className="text-overline">BADGE</span>
```

### 3. Custom Sizing
```tsx
import { Typography } from '@/components/ui/Typography';

// Using size utilities
<span className={Typography.TextSize.micro}>Very small</span>
<div className={Typography.FontWeight.semibold}>Bold text</div>
```

## Specialized Classes

### Typography Styles
- `.text-display` - 36px, bold, tight tracking
- `.text-title` - 24px, semibold, tight tracking
- `.text-headline` - 20px, semibold, snug leading
- `.text-subheading` - 18px, medium weight
- `.text-body` - 15px, normal weight, relaxed leading
- `.text-caption` - 11px, medium weight, tight leading
- `.text-overline` - 10px, bold, uppercase, wide tracking

### Button Typography
- `.btn-text` - 14px, medium weight
- `.btn-text-lg` - 16px, medium weight
- `.btn-text-sm` - 12px, medium weight

### Form Typography
- `.label-text` - 14px, medium weight, slate-700
- `.input-text` - 14px, normal weight
- `.helper-text` - 12px, slate-500
- `.error-text` - 12px, red-600, medium weight

## Examples

### Card Component
```tsx
<div className="card">
  <Typography.Headline>Project Name</Typography.Headline>
  <Typography.Body>Project description text here</Typography.Body>
  <Typography.Caption className="text-slate-500">
    Updated 2 hours ago
  </Typography.Caption>
</div>
```

### Form Component
```tsx
<div className="form-field">
  <Typography.Label htmlFor="email">Email Address</Typography.Label>
  <input className="input-text" id="email" type="email" />
  <Typography.HelperText>We'll never share your email</Typography.HelperText>
</div>
```

### Navigation Component
```tsx
<nav>
  <Typography.Overline className="text-slate-400 mb-2">
    NAVIGATION
  </Typography.Overline>
  <ul>
    <li><a className="text-sm font-medium">Dashboard</a></li>
    <li><a className="text-sm font-medium">Projects</a></li>
  </ul>
</nav>
```

## Migration Guide

### Before (Inconsistent)
```tsx
<h1 className="text-2xl font-bold">Title</h1>
<p className="text-base">Body</p>
<span className="text-xs text-gray-500">Caption</span>
```

### After (Consistent)
```tsx
<Typography.Title>Title</Typography.Title>
<Typography.Body>Body</Typography.Body>
<Typography.Caption className="text-slate-500">Caption</Typography.Caption>
```

## Best Practices

1. **Use semantic components** (`Typography.Title`) over utility classes when possible
2. **Maintain hierarchy** - Don't skip levels (Display → Headline → Body)
3. **Be consistent** - Use the same patterns across components
4. **Test readability** - Ensure good contrast and appropriate line-height
5. **Consider accessibility** - Maintain proper heading structure (h1, h2, h3...)

## Custom Properties Available

```css
:root {
  --font-size-micro: 0.625rem;      /* 10px */
  --font-size-caption: 0.6875rem;   /* 11px */
  --font-size-xs: 0.75rem;          /* 12px */
  --font-size-sm: 0.875rem;         /* 14px */
  --font-size-body: 0.9375rem;      /* 15px */
  --font-size-base: 1rem;           /* 16px */
  /* ... and more */
}
```