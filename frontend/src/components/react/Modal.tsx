import { useEffect, useState, type ReactNode } from 'react';


interface Props {
  id: string;
  children: ReactNode;
  isOpen?: boolean;
  onClose?: () => void;
}

export default function Modal({ id, children, isOpen = false, onClose }: Props) {
  const [active, setActive] = useState(isOpen);

  useEffect(() => {
    setActive(isOpen);
  }, [isOpen]);

  useEffect(() => {
    if (active) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [active]);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && active) {
        handleClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [active]);

  const handleClose = () => {
    setActive(false);
    if (onClose) {
      onClose();
    }
  };

  return (
    <div
      id={id}
      className={`modal ${active ? 'active' : ''}`}
      role="dialog"
      aria-modal="true"
      aria-labelledby={`${id}-title`}
      style={{ display: active ? 'block' : 'none' }}
    >
      <div className="modal-backdrop" onClick={handleClose}></div>
      <div className="modal-content">
        <button
          className="modal-close"
          onClick={handleClose}
          aria-label="Cerrar modal"
          title="Cerrar"
        >
          ×
        </button>
        <div className="modal-body">
          {children}
        </div>
      </div>
    </div>
  );
}
