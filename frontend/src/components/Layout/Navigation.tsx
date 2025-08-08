import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { 
  Home, 
  User, 
  Shield, 
  FileText, 
  LogOut, 
  Menu,
  X,
  Briefcase,
  Target
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavigationProps {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

export function Navigation({ isOpen, setIsOpen }: NavigationProps) {
  const { user, logout } = useAuth();
  const location = useLocation();

  const navigationItems = [
  { 
    label: 'Home', 
    path: '/', 
    icon: Home, 
    roles: ['consultant', 'admin'] 
  },
  { 
    label: 'Dashboard', 
    path: '/consultant-dashboard', 
    icon: User, 
    roles: ['consultant'] 
  },
  { 
    label: 'Admin Console', 
    path: '/admin-dashboard', 
    icon: Shield, 
    roles: ['admin'] 
  },
  { 
    label: 'Reports', 
    path: '/reports', 
    icon: FileText, 
    roles: ['admin']  
  },
  { 
    label: 'Opportunities', 
    path: '/admin/opportunities', 
    icon: Briefcase, 
    roles: ['admin'] 
  },
  { 
    label: 'My Opportunities', 
    path: '/consultant/opportunities', 
    icon: Target, 
    roles: ['consultant'] 
  },
  { 
    label: 'Profile', 
    path: '/profile', 
    icon: User, 
    roles: ['consultant', 'admin'] 
  }
];

  

  const filteredItems = navigationItems.filter(item => 
    item.roles.includes(user?.role || '')
  );

  const isActivePath = (path: string) => {
    return location.pathname === path;
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-foreground/20 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Mobile menu button */}
      <Button
        variant="outline"
        size="sm"
        className="lg:hidden fixed top-4 left-4 z-50"
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? 'Close navigation menu' : 'Open navigation menu'}
        aria-expanded={isOpen}
      >
        {isOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
      </Button>

      {/* Navigation sidebar */}
      <nav 
        className={cn(
          "fixed top-0 left-0 z-40 h-screen w-64 bg-card border-r border-border transition-transform duration-300 ease-in-out lg:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
        aria-label="Main navigation"
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-6 border-b border-border">
            <h1 className="text-xl font-bold text-primary">
              Pool CMS
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              Consultant Management
            </p>
          </div>

          {/* User info */}
          <div className="p-4 border-b border-border bg-muted/30">
            <p className="font-medium text-sm">{user?.name}</p>
            <p className="text-xs text-muted-foreground">{user?.email}</p>
            <p className="text-xs text-primary font-medium capitalize mt-1">
              {user?.role}
            </p>
          </div>

          {/* Navigation items */}
          <div className="flex-1 p-4 space-y-2">
            {filteredItems.map((item) => {
              const Icon = item.icon;
              const isActive = isActivePath(item.path);
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setIsOpen(false)}
                  className={cn(
                    "flex items-center space-x-3 w-full p-3 rounded-md text-sm font-medium transition-colors",
                    "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
                    isActive 
                      ? "bg-primary text-primary-foreground" 
                      : "text-foreground hover:bg-muted"
                  )}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <Icon className="h-4 w-4" aria-hidden="true" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>

          {/* Logout button */}
          <div className="p-4 border-t border-border">
           <Button
  variant="outline"
  className="w-full justify-start"
  onClick={() => {
    logout();
    window.location.href = "http://localhost:8080";
  }}
  aria-label="Sign out of application"
>
  <LogOut className="h-4 w-4 mr-2" aria-hidden="true" />
  Logout
</Button>
          </div>
        </div>
      </nav>
    </>
  );
}