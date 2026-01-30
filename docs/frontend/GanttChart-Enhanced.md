# Enhanced Gantt Chart - PronaFlow v5.2

## Tổng quan

Trang Gantt Chart đã được thiết kế lại hoàn toàn với trải nghiệm người dùng hiện đại, hỗ trợ đa nền tảng và tuân thủ các tiêu chuẩn accessibility WCAG 2.1 AA.

## Tính năng mới

### 🎨 Theme System
- **Dark/Light Mode**: Chuyển đổi theme tự động theo hệ thống hoặc thủ công
- **Design Tokens**: Hệ thống màu sắc và spacing nhất quán
- **High Contrast**: Tự động hỗ trợ chế độ tương phản cao

### 📱 Responsive Design
- **Mobile-First**: Tối ưu cho thiết bị di động
- **Adaptive Layout**: Tự động điều chỉnh theo kích thước màn hình
- **Touch Gestures**: Hỗ trợ cử chỉ chạm và vuốt trên mobile

### ♿ Accessibility
- **Keyboard Navigation**: Điều hướng hoàn toàn bằng bàn phím
- **Screen Reader**: Hỗ trợ đầy đủ cho trình đọc màn hình
- **ARIA Labels**: Nhãn mô tả chi tiết cho tất cả components
- **Focus Management**: Quản lý focus trong modal và popover

### ⚡ Performance
- **Virtualization**: Render chỉ các items hiển thị
- **Debounced Search**: Tìm kiếm tối ưu với debounce
- **Memoization**: Cache kết quả filter và tính toán
- **Lazy Loading**: Tải component theo nhu cầu

## Cấu trúc dự án

```
src/
├── themes/
│   ├── gantt-theme.ts          # Theme configuration
│   └── ThemeProvider.tsx       # Theme context provider
├── hooks/
│   ├── useResponsive.ts        # Responsive utilities
│   ├── useAccessibility.ts     # Accessibility hooks
│   └── usePerformance.ts       # Performance optimization
├── components/
│   └── ui/
│       ├── index.tsx           # Reusable UI components
│       └── CreateTaskModal.tsx # Task creation modal
├── pages/
│   └── Workspace/
│       ├── GanttChart.tsx      # Original component
│       └── GanttChartEnhanced.tsx # New enhanced version
└── styles/
    └── gantt-theme.css         # Custom CSS for gantt library
```

## Hướng dẫn sử dụng

### Cài đặt
```bash
# Cài đặt dependencies
npm install gantt-task-react framer-motion @radix-ui/react-dialog

# Import CSS theme
import '../styles/gantt-theme.css'
```

### Sử dụng component

```tsx
import { ThemeProvider } from '../themes/ThemeProvider';
import EnhancedGanttChart from './GanttChartEnhanced';

function App() {
  return (
    <ThemeProvider defaultTheme="light">
      <EnhancedGanttChart />
    </ThemeProvider>
  );
}
```

### Customization

#### Theme Configuration
```typescript
// Tùy chỉnh theme trong gantt-theme.ts
export const customTheme: GanttTheme = {
  colors: {
    primary: {
      500: '#your-brand-color',
      // ...
    },
    // ...
  },
  // ...
};
```

#### Responsive Breakpoints
```typescript
// Trong useResponsive.ts
export function useResponsiveGanttConfig() {
  return useResponsiveValue({
    mobile: {
      rowHeight: 40,
      listCellWidth: '200px',
      // ...
    },
    // ...
  });
}
```

## Phím tắt

| Phím tắt | Chức năng |
|----------|-----------|
| `Ctrl + N` | Tạo task mới |
| `Ctrl + F` | Focus vào ô tìm kiếm |
| `Ctrl + D` | Toggle dark mode |
| `Esc` | Đóng modal/popover |
| `Arrow Keys` | Điều hướng trong danh sách |
| `Enter/Space` | Chọn item hiện tại |
| `Tab/Shift+Tab` | Di chuyển focus |

## API Reference

### GanttChartEnhanced Props
```typescript
interface GanttChartProps {
  initialTasks?: Task[];
  onTaskCreate?: (task: Task) => void;
  onTaskUpdate?: (task: Task) => void;
  onTaskDelete?: (taskId: string) => void;
  defaultViewMode?: ViewMode;
  enableDarkMode?: boolean;
  compactMode?: boolean;
}
```

### Task Interface
```typescript
interface Task {
  id: string;
  name: string;
  start: Date;
  end: Date;
  progress: number;
  type: 'project' | 'task';
  priority?: 'URGENT' | 'HIGH' | 'NORMAL' | 'LOW';
  status?: 'TODO' | 'IN_PROGRESS' | 'REVIEW' | 'DONE';
  assignee?: string;
  project?: string;
  dependencies?: string[];
  styles: TaskStyles;
}
```

### Theme Hook
```typescript
const { theme, mode, toggleTheme, setTheme } = useTheme();
```

### Responsive Hooks
```typescript
const deviceType = useDeviceType(); // 'mobile' | 'tablet' | 'desktop'
const isMobile = useIsMobile();
const config = useResponsiveGanttConfig();
```

## Best Practices

### Performance
1. **Sử dụng useMemo cho filtered data**
2. **Debounce search input** (đã implement)
3. **Lazy load modal components**
4. **Virtualize cho > 100 tasks**

### Accessibility
1. **Luôn có ARIA labels**
2. **Maintain focus order hợp lý**
3. **Provide keyboard alternatives**
4. **Test với screen readers**

### Responsive
1. **Design mobile-first**
2. **Progressive enhancement**
3. **Touch-friendly targets (44px+)**
4. **Readable text sizes**

## Troubleshooting

### Common Issues

**CSS styles không áp dụng:**
```css
/* Đảm bảo import CSS sau gantt-task-react CSS */
import 'gantt-task-react/dist/index.css';
import '../styles/gantt-theme.css'; /* Phải sau */
```

**Theme không switching:**
```typescript
// Kiểm tra ThemeProvider wrap component
<ThemeProvider>
  <YourComponent />
</ThemeProvider>
```

**Performance issues với large datasets:**
```typescript
// Sử dụng virtualization
const { visibleItems } = useVirtualization(
  tasks, 
  containerHeight, 
  itemHeight
);
```

## Migration Guide

### Từ GanttChart.tsx cũ

1. **Thay thế imports:**
```typescript
// Cũ
import GanttChart from './GanttChart';

// Mới  
import GanttChartEnhanced from './GanttChartEnhanced';
import { ThemeProvider } from '../themes/ThemeProvider';
```

2. **Wrap với ThemeProvider:**
```typescript
<ThemeProvider>
  <GanttChartEnhanced />
</ThemeProvider>
```

3. **Update task data structure** (nếu cần)
4. **Test accessibility và responsive**

## Roadmap

- [ ] Real-time collaboration
- [ ] Advanced filtering với query builder
- [ ] Export to PDF/Excel
- [ ] Gantt chart printing
- [ ] Custom task templates
- [ ] Drag & drop file attachments
- [ ] Integration với calendar apps

## Support

Để được hỗ trợ, vui lòng:
1. Kiểm tra documentation này
2. Search trong existing issues
3. Tạo issue mới với reproduction steps
4. Tag @pronaflow-team để được hỗ trợ nhanh

---

**Version:** 5.2.0  
**Last Updated:** January 29, 2026  
**Maintainer:** PronaFlow Team