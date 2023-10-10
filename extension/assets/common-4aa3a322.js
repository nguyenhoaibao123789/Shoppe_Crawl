(function () {
	'use strict';

	const importPath = /*@__PURE__*/ JSON.parse('"../js/tool/common.js"');

	import(chrome.runtime.getURL(importPath));

})();
