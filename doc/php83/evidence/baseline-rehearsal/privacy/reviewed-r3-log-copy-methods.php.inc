	/** Return a display-only copy. Never mutate request or dispatch values. */
	public static function isSensitiveLogField($name)
	{
		$parts = explode(':', (string)$name);
		$name = strtolower(end($parts));
		return in_array($name, array('secret', 'adminsecret', 'ks', 'password',
			'oldpassword', 'newpassword', 'token', 'uploadtokenid'), true);
	}

	public static function sensitiveValueForLog($value)
	{
		return $value === null ? null : '[REDACTED]';
	}

	public static function paramsForLog(array $params, $depth = 0)
	{
		if ($depth >= 32)
			return array('__log_copy_limit__' => true);
		$copy = array();
		foreach ($params as $name => $value)
		{
			if (self::isSensitiveLogField($name))
				$copy[$name] = self::sensitiveValueForLog($value);
			elseif (is_array($value))
				$copy[$name] = self::paramsForLog($value, $depth + 1);
			elseif (is_object($value))
				$copy[$name] = self::publicObjectForLog($value, $depth + 1);
			else
				$copy[$name] = $value;
		}
		return $copy;
	}

	public static function publicObjectForLog($value, $depth = 0)
	{
		// Display view only: no clone, serialization, magic getter or constructor.
		// Non-public state is deliberately not exported by this diagnostic view.
		return array('__class__' => get_class($value),
			'__public_properties__' => self::paramsForLog(get_object_vars($value), $depth));
	}

	public static function argumentsForLog(array $arguments, array $actionParams)
	{
		// buildActionArguments appends values in the action-parameter iteration order.
		// An inconsistent log view must not throw or change actual dispatch behavior.
		if (count($arguments) !== count($actionParams) ||
			(count($arguments) && array_keys($arguments) !== range(0, count($arguments) - 1)))
			return array('__log_copy_mapping_mismatch__' => true);
		$copy = array();
		$index = 0;
		foreach ($actionParams as $param)
		{
			if (!is_object($param) || !method_exists($param, 'getName'))
				return array('__log_copy_mapping_mismatch__' => true);
			$value = $arguments[$index];
			if (self::isSensitiveLogField($param->getName()))
				$copy[$index] = self::sensitiveValueForLog($value);
			elseif (is_array($value))
				$copy[$index] = self::paramsForLog($value);
			elseif (is_object($value))
				$copy[$index] = self::publicObjectForLog($value);
			else
				$copy[$index] = $value;
			$index++;
		}
		return $copy;
	}

