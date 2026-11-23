# Messages to the user

Wording for common situations, so answers are consistent for everyone.

**Table has no description:**
> `demo.<table>` has an empty `COMMENT`, so I can't confirm it fits. Show the structure and a sample?

**No access to a layer:**
> The connector's role has no access to this layer. Reported numbers come from `mart` anyway;
> if the raw layer is really needed, access is granted by the DWH owner.

**A raw layer was used:**
> This is `raw.<table>` - currencies, duplicates and test records are not filtered out, so it
> can't be presented as a reported number. For the report I'll use `demo.<table>`.

**Asked to modify data:**
> Warehouse access is read-only: I can't change or delete data. Data engineers
> do that - I can draft the task description.

**Incomplete window:**
> `demo.<table>` has data through <data_through>; the last <N> days of the window aren't loaded yet.

**Incompatible types in `UNION`:**
> The `UNION` branches return columns of different types. I'll split them into separate queries
> and build the summary from those.
