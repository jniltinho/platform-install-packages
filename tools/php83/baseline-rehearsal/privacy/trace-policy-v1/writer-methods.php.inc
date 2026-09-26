	/** Render a display copy only; retain the original Throwable and event. */
	protected function _write($event)
	{
		if (isset($event['message']) && $event['message'] instanceof Throwable)
			$event['message'] = self::throwableForLog($event['message']);
		parent::_write($event);
	}

	private static function throwableForLog(Throwable $error)
	{
		$chain = array();
		do
		{
			$text = get_class($error) . ': ' . $error->getMessage() .
				' [code=' . $error->getCode() . '] in ' . $error->getFile() . ':' . $error->getLine();
			$text .= "\nStack trace:";
			foreach ($error->getTrace() as $index => $frame)
			{
				$location = isset($frame['file']) ? $frame['file'] . ':' . $frame['line'] : '[internal function]';
				$call = (isset($frame['class']) ? $frame['class'] : '') .
					(isset($frame['type']) ? $frame['type'] : '') .
					(isset($frame['function']) ? $frame['function'] : '');
				$args = array();
				if (isset($frame['args']))
					foreach ($frame['args'] as $argument)
						$args[] = '[REDACTED:' . gettype($argument) . ']';
				$text .= "\n#" . $index . ' ' . $location . ': ' . $call . '(' . implode(', ', $args) . ')';
			}
			$text .= "\n#" . count($error->getTrace()) . ' {main}';
			$chain[] = $text;
			$error = $error->getPrevious();
		} while ($error !== null);
		// Preserve every previous exception, oldest first like native display.
		return implode("\n\nNext ", array_reverse($chain));
	}

