import React from 'react';
import { cva } from 'class-variance-authority';

export const Button = ({ children, className, ...props }) => (
  <button
    className={`px-4 py-2 rounded-md font-semibold text-white transition-colors ${className}`}
    {...props}
  >
    {children}
  </button>
);

export const Input = ({ className, ...props }) => (
  <input
    className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${className}`}
    {...props}
  />
);

export const TextArea = ({ className, ...props }) => (
  <textarea
    className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${className}`}
    {...props}
  />
);

export const Select = ({ children, className, ...props }) => (
  <select
    className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${className}`}
    {...props}
  >
    {children}
  </select>
);

export const Spinner = () => (
  <div className="flex justify-center items-center">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
  </div>
);

export const Card = ({ children, className, ...props }) => (
  <div
    className={`bg-white shadow-md rounded-lg p-6 ${className}`}
    {...props}
  >
    {children}
  </div>
);

export const Heading = ({ level = 2, children, className, ...props }) => {
  const Tag = `h${level}`;
  const baseStyle = 'font-bold mb-4';
  const styles = {
    1: 'text-3xl',
    2: 'text-2xl',
    3: 'text-xl',
    4: 'text-lg',
  };

  return (
    <Tag className={`${baseStyle} ${styles[level]} ${className}`} {...props}>
      {children}
    </Tag>
  );
};