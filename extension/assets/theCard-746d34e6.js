(function () {
	'use strict';

	const importPath = /*@__PURE__*/ JSON.parse('"../js/tool/theCard.js"');

	import(chrome.runtime.getURL(importPath));

})();
