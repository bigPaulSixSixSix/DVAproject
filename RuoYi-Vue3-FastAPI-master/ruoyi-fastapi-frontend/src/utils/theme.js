// 处理主题样式
export function handleThemeStyle(theme) {
	const isDark = document.documentElement.classList.contains('dark')
	document.documentElement.style.setProperty('--el-color-primary', theme)
	
	// 在深色模式下，移除内联样式，让 Element Plus 自己处理颜色变量
	// 这样 Element Plus 的深色模式颜色变量可以正常工作
	if (isDark) {
		// 移除内联样式，让 Element Plus 的深色模式变量生效
		for (let i = 1; i <= 9; i++) {
			document.documentElement.style.removeProperty(`--el-color-primary-light-${i}`)
		}
		// 仍然设置 dark 变量，以备需要
		for (let i = 1; i <= 9; i++) {
			document.documentElement.style.setProperty(`--el-color-primary-dark-${i}`, `${getDarkColor(theme, i / 10)}`)
		}
	} else {
		// 浅色模式下，设置 light 变量
		for (let i = 1; i <= 9; i++) {
			document.documentElement.style.setProperty(`--el-color-primary-light-${i}`, `${getLightColor(theme, i / 10)}`)
		}
		// 仍然设置 dark 变量，以备需要
		for (let i = 1; i <= 9; i++) {
			document.documentElement.style.setProperty(`--el-color-primary-dark-${i}`, `${getDarkColor(theme, i / 10)}`)
		}
	}
}

// hex颜色转rgb颜色
export function hexToRgb(str) {
	str = str.replace('#', '')
	let hexs = str.match(/../g)
	for (let i = 0; i < 3; i++) {
		hexs[i] = parseInt(hexs[i], 16)
	}
	return hexs
}

// rgb颜色转Hex颜色
export function rgbToHex(r, g, b) {
	let hexs = [r.toString(16), g.toString(16), b.toString(16)]
	for (let i = 0; i < 3; i++) {
		if (hexs[i].length == 1) {
			hexs[i] = `0${hexs[i]}`
		}
	}
	return `#${hexs.join('')}`
}

// 变浅颜色值
export function getLightColor(color, level) {
	let rgb = hexToRgb(color)
	for (let i = 0; i < 3; i++) {
		rgb[i] = Math.floor((255 - rgb[i]) * level + rgb[i])
	}
	return rgbToHex(rgb[0], rgb[1], rgb[2])
}

// 变深颜色值
export function getDarkColor(color, level) {
	let rgb = hexToRgb(color)
	for (let i = 0; i < 3; i++) {
		rgb[i] = Math.floor(rgb[i] * (1 - level))
	}
	return rgbToHex(rgb[0], rgb[1], rgb[2])
}
