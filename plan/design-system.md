# Design System - Modern Blogging Platform

## Theme Selection

**Theme: Ocean Blue**
- Professional, trustworthy, and content-focused
- Optimized for reading and long-form content
- Clean aesthetic suitable for modern blogging platforms
- Excellent contrast for dashboard interfaces and role-based features

## Foundations

### Color Tokens

**Light Mode:**
- Primary: `hsl(200, 84%, 42%)` - Rich blue for CTAs, links, interactive elements
- Background: `hsl(0, 0%, 98%)` - Very light gray for main background
- Card: `hsl(0, 0%, 100%)` - Pure white for article cards, modals, content containers
- Text: `hsl(0, 0%, 12%)` - Very dark gray for body text and headings
- Text Secondary: `hsl(0, 0%, 45%)` - Medium gray for metadata, captions, timestamps
- Secondary: `hsl(200, 84%, 42%)` - Rich blue for secondary buttons, badges
- Border: `hsl(0, 0%, 88%)` - Light gray for dividers, card borders, input borders
- Muted: `hsl(0, 0%, 94%)` - Very light gray for disabled states, subtle backgrounds
- Accent: `hsl(180, 84%, 45%)` - Teal for highlights, notifications, featured badges
- Success: `hsl(142, 71%, 45%)` - Green for success states, publish confirmations
- Warning: `hsl(38, 92%, 50%)` - Orange for warnings, drafts, pending states
- Error: `hsl(0, 84%, 60%)` - Red for errors, delete confirmations

**Dark Mode:**
- Primary: `hsl(200, 84%, 42%)` - Rich blue (consistent across modes)
- Background: `hsl(0, 0%, 9%)` - Very dark gray for main background
- Card: `hsl(0, 0%, 14%)` - Dark gray for article cards, modals, content containers
- Text: `hsl(0, 0%, 95%)` - Very light gray for body text and headings
- Text Secondary: `hsl(0, 0%, 65%)` - Light gray for metadata, captions, timestamps
- Secondary: `hsl(200, 84%, 42%)` - Rich blue (consistent across modes)
- Border: `hsl(0, 0%, 22%)` - Medium dark gray for dividers, card borders
- Muted: `hsl(0, 0%, 18%)` - Dark gray for disabled states, subtle backgrounds
- Accent: `hsl(180, 84%, 45%)` - Teal (consistent across modes)
- Success: `hsl(142, 71%, 45%)` - Green (consistent across modes)
- Warning: `hsl(38, 92%, 50%)` - Orange (consistent across modes)
- Error: `hsl(0, 84%, 60%)` - Red (consistent across modes)

**Usage Guidelines:**
- Primary: Main CTAs, publish buttons, primary navigation active states
- Secondary: Secondary actions, role badges (Writer, Admin), tag buttons
- Accent: Featured article badges, trending indicators, notification dots
- Success: Published status, successful operations, like confirmations
- Warning: Draft status, unpublished warnings, pending reviews
- Error: Delete confirmations, validation errors, failed operations

### Typography Scale

**Font Family:**
- Primary: `Inter` - Clean, highly readable for UI and body text
- Headings: `Inter` - Consistent with body for modern aesthetic
- Code/Monospace: `'Fira Code', monospace` - For code snippets in articles

**Type Scale:**
- Display: 3.5rem (56px) / Bold / 1.1 line-height - Hero headings on homepage
- H1: 2.5rem (40px) / Bold / 1.2 line-height - Article titles
- H2: 2rem (32px) / Semibold / 1.3 line-height - Section headings, dashboard titles
- H3: 1.5rem (24px) / Semibold / 1.4 line-height - Article subheadings, card titles
- H4: 1.25rem (20px) / Medium / 1.5 line-height - Component headings
- Body Large: 1.125rem (18px) / Regular / 1.7 line-height - Article body text
- Body: 1rem (16px) / Regular / 1.6 line-height - UI text, descriptions
- Body Small: 0.875rem (14px) / Regular / 1.5 line-height - Metadata, captions, timestamps
- Caption: 0.75rem (12px) / Medium / 1.4 line-height - Labels, badges, micro-copy

**Reading Optimization:**
- Article body text: Body Large with 65-75 characters per line max width
- Paragraph spacing: 1.5em between paragraphs
- Heading margin: 2em top, 0.5em bottom

### Spacing & Grid

**Spacing Scale (4px base unit):**
- xs: 4px - Tight spacing, icon gaps
- sm: 8px - Component padding, small gaps
- md: 16px - Card padding, standard gaps
- lg: 24px - Section spacing, card gaps
- xl: 32px - Large section spacing
- 2xl: 48px - Page section dividers
- 3xl: 64px - Major layout sections
- 4xl: 96px - Hero sections, landing page spacing

**Grid System:**
- Container max-width: 1280px (dashboard), 800px (article content)
- Columns: 12-column responsive grid
- Gutter: 24px (desktop), 16px (mobile)
- Breakpoints: mobile (< 640px), tablet (640-1024px), desktop (> 1024px)

**Layout Patterns:**
- Homepage: 3-column grid for featured articles (desktop), 1-column (mobile)
- Article page: Single column with max-width 800px, centered
- Dashboards: Sidebar navigation (240px) + main content area
- Instagram widget: 3x3 grid on desktop, 2x2 on tablet, 1x3 on mobile

### Iconography

**Icon Library:** Lucide React
- Size scale: 16px (small), 20px (medium), 24px (large), 32px (xlarge)
- Stroke width: 2px (standard), 1.5px (light for large icons)
- Usage: Navigation icons, action buttons, status indicators, social media icons

**Common Icons:**
- Navigation: Home, Pen, User, Settings, LogOut
- Actions: Heart, MessageCircle, Share2, Bookmark, MoreVertical
- Status: Check, AlertCircle, Info, TrendingUp
- Social: Instagram, Twitter, Facebook, Link
- Editor: Bold, Italic, Image, Code, List

## Theming

### Light/Dark Mode Mapping

**Automatic Theme Detection:**
- Detect system preference on initial load
- User toggle persists in localStorage
- Smooth transition: 0.3s ease on color properties

**Component Adaptations:**
- Article cards: Subtle shadow in light, border emphasis in dark
- Navigation: Transparent background with backdrop blur in both modes
- Dashboards: Sidebar maintains contrast in both modes
- Instagram widget: Overlay gradients adjust for mode
- Code blocks: Syntax highlighting themes switch with mode

### Role-Based Visual Indicators

**Admin Role:**
- Badge color: Error color with white text
- Dashboard accent: Error color for admin-only features
- Navigation highlight: Error color for admin menu items

**Writer Role:**
- Badge color: Warning color with dark text
- Dashboard accent: Warning color for writer features
- Navigation highlight: Warning color for writer menu items

**Reader Role:**
- Badge color: Secondary color with white text
- Profile accent: Secondary color for reader features

## Animation & Micro-interactions

**Interaction Principles:**
- Smooth and subtle - avoid distracting from content
- Purposeful feedback - confirm user actions
- Performance-conscious - use CSS transforms, avoid layout shifts

**Hover States:**
- Article cards: Lift effect (translateY(-4px)) + shadow increase, 0.2s ease
- Buttons: Background darken (10%), scale(1.02), 0.15s ease
- Links: Color shift to accent, underline animation from left, 0.2s ease
- Navigation items: Background fade-in, 0.2s ease

**Loading States:**
- Skeleton screens: Shimmer animation for article cards, 1.5s ease infinite
- Spinners: Rotate animation for buttons, 0.8s linear infinite
- Progress bars: Linear gradient animation for uploads, 1s ease infinite

**Transitions:**
- Page transitions: Fade in + slide up (20px), 0.3s ease
- Modal/Dialog: Scale from 0.95 + fade in, 0.2s ease
- Notifications: Slide in from top + fade, 0.3s ease-out
- Like animation: Heart scale(1.2) + color change, 0.3s cubic-bezier

**Scroll Animations:**
- Article cards: Fade in + slide up on viewport enter, stagger 0.1s
- Instagram widget: Grid items fade in sequentially, 0.05s stagger
- Featured section: Parallax subtle movement on scroll

**Micro-interactions:**
- Like button: Heart fill animation + bounce effect + count increment
- Comment submit: Success checkmark animation + comment appear
- Save draft: Auto-save indicator pulse
- Publish button: Confetti animation on successful publish
- Search input: Expand width on focus, 0.3s ease

## Dark Mode & Color Contrast Rules (Critical)

**Always use explicit colors - never rely on browser defaults or component variants like 'variant="outline"'**

**Force dark mode with CSS:**
```css
html { color-scheme: dark; }
```
```html
<meta name="color-scheme" content="dark">
```

**Contrast Ratios:**
- Minimum 4.5:1 for normal text
- Minimum 3:1 for large text (18px+ or 14px+ bold)
- Minimum 3:1 for interactive components

**Override browser defaults with !important for form elements:**
```css
input, textarea, select {
  background-color: #000000 !important;
  color: #ffffff !important;
}
```

**Testing Requirements:**
- Test in both light and dark system modes
- System dark mode can override custom styling
- Use semantic color classes instead of component variants
- Example: `className="bg-gray-800 text-gray-300 border border-gray-600"` NOT `variant="outline"`

**CSS Custom Properties:**
Create consistent custom properties for reusable colors across components

**Quick Debugging:**
1. Check if using `variant="outline"` - replace with explicit colors
2. Add explicit colors to all interactive elements
3. Use `!important` if browser defaults persist
4. Test with system light and dark modes

### Color Contrast Checklist (apply to all components):

- [ ] No `variant="outline"` or similar browser-dependent styles
- [ ] Explicit background and text colors specified
- [ ] High contrast ratios (4.5:1+ for text, 3:1+ for large text)
- [ ] Tested with system dark mode ON and OFF
- [ ] Form elements have forced dark styling
- [ ] Badges and buttons use custom classes, not default variants
- [ ] Placeholder text has proper contrast (minimum 4.5:1)
- [ ] Focus states are visible and accessible (minimum 3:1 contrast with background)
- [ ] Article body text maintains 4.5:1 contrast in both modes
- [ ] Dashboard sidebar navigation items meet contrast requirements
- [ ] Role badges (Admin/Writer/Reader) have sufficient contrast
- [ ] Instagram widget overlay text is readable in both modes
- [ ] Comment section maintains readability in dark mode
- [ ] Like/heart icons and counts are clearly visible
- [ ] Notification indicators meet 3:1 contrast minimum
