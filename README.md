# Worthy api

## How to start

```bash
# Setup python

pyenv install 3.13.2
# if it already exists dont install

pyenv local 3.13.2
# check with python --version

# Setup poetry

# check if it's already installed 
poetry -V
# should output "Poetry (version 2.1.1)"

# if not installed
curl -sSL https://install.python-poetry.org | python3 -

# Activate poetry env
eval $(poetry env activate)

# U are ready to go :)
```

## Tech Stack

- pyenv
- poetry
- fastapi
- sqlalchemy (Declarative syntax, with DeclarativeBase)


## TODO
```
-- dataase schema
CREATE TABLE users (
    primary_currency TEXT NOT NULL DEFAULT 'BYN',
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    image TEXT NOT NULL,
    id INTEGER PRIMARY KEY NOT NULL,
    balance INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE transactions (
    description TEXT NOT NULL,
    currency TEXT NOT NULL,
    id INTEGER PRIMARY KEY NOT NULL,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    is_income INTEGER NOT NULL,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000)
    -- * 1000 for ms-based
);

CREATE TABLE tags (
    text TEXT NOT NULL,
    id INTEGER PRIMARY KEY NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_id INTEGER NOT NULL REFERENCES transactions(id) ON DELETE CASCADE
);
```


```
# users router
export const usersRouter = createTRPCRouter({
    me: protectedProcedure.query(async ({ ctx }) => {
        const usersRes = await ctx.db
            .select()
            .from(usersTable)
            .where(eq(usersTable.id, ctx.session.user.id))
            .limit(1);

        if (!usersRes[0]) {
            throw new TRPCError({
                code: 'NOT_FOUND',
                message: 'User not found.',
            });
        }

        const { password: _, ...rest } = usersRes[0];
        return rest;
    }),

    getBalance: protectedProcedure.query(async ({ ctx }) => {
        const res = await ctx.db
            .select({
                balance: usersTable.balance,
                currency: usersTable.primaryCurrency,
            })
            .from(usersTable)
            .where(eq(usersTable.id, ctx.session.user.id))
            .limit(1);

        if (!res[0]) {
            throw new TRPCError({
                code: 'NOT_FOUND',
                message: 'User not found.',
            });
        }

        res[0].balance /= 100;
        return res[0];
    }),
});
```

```
# transactions router
export const transactionsRouter = createTRPCRouter({
    getSingle: protectedProcedure
        .input(z.number())
        .query(async ({ ctx, input }) => {
            const resp = await ctx.db
                .select()
                .from(transactionsTable)
                .where(and(
                    eq(transactionsTable.id, input),
                    eq(transactionsTable.ownerId, ctx.session.user.id),
                ));

            if (!resp[0]) {
                return null;
            }

            return {
                ...resp[0],
                amount: resp[0].amount / 100,
            };
        }),
    delete: protectedProcedure
        .input(z.number())
        .mutation(async ({ ctx, input }) => {
            const transaction = await ctx.db
                .select({
                    amount: transactionsTable.amount,
                    isIncome: transactionsTable.isIncome,
                })
                .from(transactionsTable)
                .where(and(
                    eq(transactionsTable.id, input),
                    eq(transactionsTable.ownerId, ctx.session.user.id),
                ));

            if (!transaction[0]) {
                return false;
            }

            const formatted = transaction[0].amount;
            if (transaction[0].isIncome) {
                await ctx.db
                    .update(usersTable)
                    .set({ balance: sql`${usersTable.balance} - ${formatted}` })
                    .where(eq(usersTable.id, ctx.session.user.id));
            } else {
                await ctx.db
                    .update(usersTable)
                    .set({ balance: sql`${usersTable.balance} + ${formatted}` })
                    .where(eq(usersTable.id, ctx.session.user.id));
            }

            await ctx.db
                .delete(transactionsTable)
                .where(eq(transactionsTable.id, input));

            return true;
        }),
    getList: protectedProcedure
        .input(z.object({
            page: z.number(),
            perPage: z.number(),
            description: z.string().optional(),
            tags: z.array(z.string()).optional(),
            startDate: z.number().optional(),
            endDate: z.number().optional(),
        }))
        .query(async ({ ctx, input }) => {
            type Transaction = Omit<typeof transactionsTable.$inferSelect, 'ownerId'>;

            // if tags in input create this 2 sub queries that eval into [tr.id]
            let tagsCondition: SQL<unknown>;
            if (input.tags?.length) {
                const wildcard = '%' + input.tags.map(() => ',').slice(0, -1).join('%') + '%';
                const sq1 = ctx.db
                    .select({
                        transaction_id: tagsTable.transactionId,
                        matched_tags_str: sql`GROUP_CONCAT(${tagsTable.text})`.as('matched_tags_str'),
                    })
                    .from(tagsTable)
                    .where(inArray(tagsTable.text, input.tags))
                    .groupBy(tagsTable.transactionId)
                    .as('sq1');
                const sq2 = ctx.db
                    .select({
                        transaction_id: sq1.transaction_id,
                    })
                    .from(sq1)
                    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
                    // @ts-ignore - according to drizzleOrm docs, aliased field is used correctly, but aliased have different signature
                    .where(like(sq1.matched_tags_str, wildcard));
                tagsCondition = inArray(transactionsTable.id, sq2);
            } else {
                tagsCondition = sql`1=1`;
            }

            // main query
            const resp: (Transaction & { tags: string | null })[] = await ctx.db.select({
                    id: transactionsTable.id,
                    isIncome: transactionsTable.isIncome,
                    amount: transactionsTable.amount,
                    currency: transactionsTable.currency,
                    description: transactionsTable.description,
                    createdAt: transactionsTable.createdAt,
                    tags: sql<string | null>`GROUP_CONCAT(${tagsTable.text})`.as('tags'),
                })
                .from(transactionsTable)
                .where(and(
                    eq(transactionsTable.ownerId, ctx.session.user.id),
                    like(transactionsTable.description, `%${input.description}%`),
                    gte(transactionsTable.createdAt, new Date(input.startDate ?? 1)),
                    lte(transactionsTable.createdAt,
                        input.endDate !== -1 && input.endDate !== undefined
                            ? new Date(input.endDate)
                            : new Date()
                    ),
                    tagsCondition,
                ))
                .offset((input.page - 1) * input.perPage)
                .groupBy(transactionsTable.id)
                .orderBy(desc(transactionsTable.createdAt))
                .limit(input.perPage)
                .leftJoin(tagsTable, eq(tagsTable.transactionId, transactionsTable.id));

            // adjusting response
            const result = resp.reduce((acc, el) => {
                const tags = el.tags?.split(',') ?? [];
                return [
                    ...acc,
                    {
                        ...el,
                        tags: tags,
                        amount: el.amount / 100,
                    },
                ];
            }, [] as (Transaction & { tags: string[] })[]);

            return result;
        }),
    getRecent: protectedProcedure.query(async ({ ctx }) => {
        const resp = await ctx.db
            .select()
            .from(transactionsTable)
            .where(eq(transactionsTable.ownerId, ctx.session.user.id))
            .orderBy(desc(transactionsTable.createdAt))
            .limit(3);


        return resp?.map(el => {
            return {
                ...el,
                amount: el.amount / 100,
            };
        });
    }),

    create: protectedProcedure
        .input(TransactionCreateSchema
            .omit({ ownerId: true })
            .extend({ tags: z.array(z.string()) }),
        )
        .mutation(async ({ ctx, input }) => {
            // TODO use Transaction
            const { tags, ...rest } = input;
            const formatted = Math.floor(input.amount * 100);
            const toInsert: (typeof transactionsTable.$inferInsert) = {
                ...rest,
                amount: formatted,
                ownerId: ctx.session.user.id,
            };

            const resp = await ctx.db
                .insert(transactionsTable)
                .values(toInsert)
                .returning({ insertedId: transactionsTable.id });

            if (input.isIncome) {
                await ctx.db
                    .update(usersTable)
                    .set({ balance: sql`${usersTable.balance} + ${formatted}` })
                    .where(eq(usersTable.id, ctx.session.user.id));
            } else {
                await ctx.db
                    .update(usersTable)
                    .set({ balance: sql`${usersTable.balance} - ${formatted}` })
                    .where(eq(usersTable.id, ctx.session.user.id));
            }

            if (!tags?.length) {
                return true;
            }

            const tagsValues: (typeof tagsTable.$inferInsert)[] = tags.map((el) => {
                return {
                    transactionId: Number(resp[0]!.insertedId),
                    text: el,
                };
            });

            await ctx.db
                .insert(tagsTable)
                .values(tagsValues);

            return true;
        }),
});
```

```
# auth router
export const authRouter = createTRPCRouter({
    login: publicProcedure.input(z.object({
        username: z.string(),
        password: z.string(),
    })).query(async ({ ctx, input }) => {
        const usersRes = await ctx.db.select().from(usersTable).where(eq(usersTable.username, input.username));

        const user = usersRes[0];
        if (!user) {
            throw new TRPCError({
                code: 'NOT_FOUND',
                message: 'User not found.',
            });
        }

        const isValid = await bcrypt.compare(input.password, user.password);

        if (!isValid) {
            throw new TRPCError({
                code: 'UNAUTHORIZED',
                message: 'Invalid password.',
            });
        }

        const { password: _, ...rest } = user;
        return rest;
    }),

    register: publicProcedure.input(z.object({
        username: z.string(),
        password: z.string(),
        image: z.string().optional(),
    })).mutation(async ({ ctx, input }) => {
        const usersRes = await ctx.db.select().from(usersTable).where(eq(usersTable.username, input.username));

        if (usersRes.length > 0) {
            throw new TRPCError({
                code: 'BAD_REQUEST',
                message: 'User already exists.',
            });
        }

        const password = await bcrypt.hash(input.password, SALT_ROUNDS);
        input.image = input.image ?? `https://api.dicebear.com/7.x/identicon/svg?seed=${encodeURIComponent(input.username)}`;

        await ctx.db.insert(usersTable).values({
            username: input.username,
            password: password,
            image: input.image,
        });

        return true;
    }),
});
```