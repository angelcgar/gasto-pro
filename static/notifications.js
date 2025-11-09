/**
 * Sistema de notificaciones Toast
 * No causa saltos en la UI, aparece como overlay
 */

const ToastNotification = {
	// Configuración
	config: {
		duration: 3000, // 3 segundos por defecto
		position: "top-right", // posición del toast
	},

	// Mapeo de tipos a iconos y títulos
	types: {
		success: {
			icon: "✓",
			title: "Éxito",
		},
		error: {
			icon: "✕",
			title: "Error",
		},
		warning: {
			icon: "⚠",
			title: "Advertencia",
		},
		info: {
			icon: "ℹ",
			title: "Información",
		},
	},

	/**
	 * Muestra una notificación toast
	 * @param {string} message - Mensaje a mostrar
	 * @param {string} type - Tipo de notificación (success, error, warning, info)
	 * @param {number} duration - Duración en ms (opcional)
	 */
	show(message, type = "info", duration = null) {
		const finalDuration = duration || this.config.duration;
		const typeConfig = this.types[type] || this.types.info;

		// Crear contenedor si no existe
		let container = document.querySelector(".toast-container");
		if (!container) {
			container = document.createElement("div");
			container.className = "toast-container";
			document.body.appendChild(container);
		}

		// Crear el toast
		const toast = this.createToast(message, type, typeConfig);
		container.appendChild(toast);

		// Auto-cerrar después de la duración especificada
		const timeoutId = setTimeout(() => {
			this.hide(toast);
		}, finalDuration);

		// Permitir cerrar manualmente
		const closeBtn = toast.querySelector(".toast-close");
		closeBtn.addEventListener("click", () => {
			clearTimeout(timeoutId);
			this.hide(toast);
		});

		// Animar entrada
		setTimeout(() => toast.classList.add("show"), 10);
	},

	/**
	 * Crea el elemento DOM del toast
	 */
	createToast(message, type, typeConfig) {
		const toast = document.createElement("div");
		toast.className = `toast-notification toast-${type}`;

		toast.innerHTML = `
      <div class="toast-header-custom">
        <span class="toast-icon">${typeConfig.icon}</span>
        <strong class="toast-title">${typeConfig.title}</strong>
        <button type="button" class="toast-close" aria-label="Cerrar">×</button>
      </div>
      <div class="toast-body-custom">${message}</div>
      <div class="toast-progress">
        <div class="toast-progress-bar" style="color: ${this.getProgressColor(type)}"></div>
      </div>
    `;

		return toast;
	},

	/**
	 * Oculta y elimina un toast
	 */
	hide(toast) {
		toast.classList.add("hiding");
		setTimeout(() => {
			toast.remove();

			// Eliminar contenedor si no hay más toasts
			const container = document.querySelector(".toast-container");
			if (container && container.children.length === 0) {
				container.remove();
			}
		}, 300); // Tiempo de la animación de salida
	},

	/**
	 * Obtiene el color de la barra de progreso según el tipo
	 */
	getProgressColor(type) {
		const colors = {
			success: "#27ae60",
			error: "#e74c3c",
			warning: "#f39c12",
			info: "#16a085",
		};
		return colors[type] || colors.info;
	},

	// Métodos de acceso rápido
	success(message, duration) {
		this.show(message, "success", duration);
	},

	error(message, duration) {
		this.show(message, "error", duration);
	},

	warning(message, duration) {
		this.show(message, "warning", duration);
	},

	info(message, duration) {
		this.show(message, "info", duration);
	},
};

// Hacer disponible globalmente
window.Toast = ToastNotification;

/**
 * Función auxiliar para procesar mensajes flash de Flask
 * y convertirlos en toasts
 */
document.addEventListener("DOMContentLoaded", function () {
	// Buscar mensajes flash tradicionales y convertirlos en toasts
	const flashMessages = document.querySelectorAll("[data-flash-message]");

	flashMessages.forEach((element) => {
		const message = element.getAttribute("data-flash-message");
		const type = element.getAttribute("data-flash-type") || "info";

		// Mostrar como toast
		Toast.show(message, type);

		// Eliminar el elemento original (ya no se necesita)
		element.remove();
	});
});
