import React from "react";
import styles from "./ui.module.css";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
  fullWidth?: boolean;
  children: React.ReactNode;
}

export function Button({
  variant = "primary",
  size = "md",
  fullWidth = false,
  className = "",
  children,
  ...props
}: ButtonProps) {
  const classes = [
    styles.button,
    variant === "primary" && styles.btnPrimary,
    variant === "secondary" && styles.btnSecondary,
    variant === "danger" && styles.btnDanger,
    variant === "ghost" && styles.btnGhost,
    size === "sm" && styles.btnSm,
    size === "md" && styles.btnMd,
    size === "lg" && styles.btnLg,
    fullWidth && styles.btnFull,
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <button className={classes} {...props}>
      {children}
    </button>
  );
}
