import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Server,
  GitBranch,
  Shield,
  Key,
  Upload,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

interface NavItem {
  label: string;
  path: string;
  icon: React.ReactNode;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const sections: NavSection[] = [
  {
    title: 'Browse',
    items: [
      { label: 'Dashboard', path: '/', icon: <LayoutDashboard size={18} /> },
      { label: 'Assets', path: '/assets', icon: <Server size={18} /> },
      { label: 'Relationships', path: '/relationships', icon: <GitBranch size={18} /> },
    ],
  },
  {
    title: 'Compliance',
    items: [
      { label: 'Security Boundaries', path: '/security', icon: <Shield size={18} /> },
      { label: 'Licenses', path: '/licenses', icon: <Key size={18} /> },
    ],
  },
  {
    title: 'Admin',
    items: [
      { label: 'Data Wizard', path: '/data-wizard', icon: <Upload size={18} /> },
    ],
  },
];

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  isMobile?: boolean;
  mobileOpen?: boolean;
  onMobileClose?: () => void;
}

export default function Sidebar({ collapsed, onToggle, isMobile, mobileOpen, onMobileClose }: SidebarProps) {
  const showLabels = isMobile || !collapsed;

  return (
    <aside
      className={`fixed top-14 left-0 bottom-0 bg-white border-r border-eaw-border z-40 flex flex-col transition-all duration-200 ${
        isMobile
          ? `w-56 ${mobileOpen ? 'translate-x-0' : '-translate-x-full'}`
          : collapsed ? 'w-12' : 'w-56'
      }`}
    >
      {/* Collapse Toggle — desktop only */}
      {!isMobile && (
        <div className={`flex items-center border-b border-eaw-border ${
          collapsed ? 'justify-center p-3' : 'justify-between px-4 py-3'
        }`}>
          {!collapsed && (
            <span className="text-sm font-medium text-eaw-muted">Navigation</span>
          )}
          <button
            onClick={onToggle}
            className="p-1 hover:bg-gray-100 rounded transition-colors text-eaw-muted hover:text-eaw-font"
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={16} />}
          </button>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-2">
        {sections.map((section) => (
          <div key={section.title} className="mb-2">
            {showLabels && (
              <div className="px-4 py-2 text-[10px] font-semibold uppercase tracking-widest text-eaw-muted">
                {section.title}
              </div>
            )}
            {section.items.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                onClick={() => isMobile && onMobileClose?.()}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 mx-1 rounded text-sm font-medium transition-colors min-h-[44px] ${
                    isActive
                      ? 'bg-eaw-primary text-white'
                      : 'text-eaw-font hover:bg-gray-100'
                  } ${!isMobile && collapsed ? 'justify-center' : ''}`
                }
                title={!isMobile && collapsed ? item.label : undefined}
              >
                <span className="flex-shrink-0">{item.icon}</span>
                {showLabels && <span>{item.label}</span>}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>
    </aside>
  );
}
