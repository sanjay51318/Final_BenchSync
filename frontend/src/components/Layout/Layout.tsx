import React, { useState } from 'react';
import { Navigation } from './Navigation';
import { cn } from '@/lib/utils';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const [isNavOpen, setIsNavOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      <Navigation isOpen={isNavOpen} setIsOpen={setIsNavOpen} />
      
      {/* Main content */}
      <main 
        className={cn(
          "transition-all duration-300 ease-in-out min-h-screen",
          "lg:ml-64 pt-16 lg:pt-0"
        )}
      >
        <div className="p-6">
          {children}
        </div>
      </main>
    </div>
  );
}